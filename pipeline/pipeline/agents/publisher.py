"""Agent 5 — Publisher.

Steps:
  1. Read the EpisodeScript JSON (Agent 2 → Agent 3 output).
  2. PublisherWriter (Claude) -> PublishPackage (metadata + thumbnail spec).
  3. Save thumbnail spec to public/thumbnails/<id>.json.
  4. Render thumbnail via `npx remotion still Thumbnail`.
  5. (optional) Upload MP4 + thumbnail to YouTube via OAuth-authorized API.

Default privacy is `private`. Pass --privacy=unlisted or --privacy=public to
override after you've reviewed the rendered video.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from pipeline.agents.publisher_writer import PublisherWriter
from pipeline.agents.renderer import REMOTION_PROJECT, Renderer
from pipeline.schemas import (
    EpisodeScript,
    PrivacyStatus,
    PublishPackage,
)


@dataclass
class PublishResult:
    package: PublishPackage
    thumbnail_png: Path
    thumbnail_spec_json: Path
    video_path: Optional[Path]
    video_id: Optional[str]
    watch_url: Optional[str]
    thumbnail_set: bool


class PublisherAgent:
    def __init__(
        self,
        public_dir: Optional[Path] = None,
        out_dir: Optional[Path] = None,
        writer: Optional[PublisherWriter] = None,
        renderer: Optional[Renderer] = None,
    ) -> None:
        self.public_dir = public_dir or REMOTION_PROJECT / "public"
        self.out_dir = out_dir or REMOTION_PROJECT / "out"
        self.writer = writer or PublisherWriter()
        self.renderer = renderer or Renderer()

    # ---------- public API ---------- #

    def publish(
        self,
        script: EpisodeScript,
        *,
        video_path: Optional[Path] = None,
        privacy: Optional[PrivacyStatus] = None,
        upload: bool = False,
        thumbnail_scale: Optional[float] = None,
        publish_at: Optional[datetime] = None,
    ) -> PublishResult:
        # 1. Generate metadata + thumbnail spec via Claude.
        result = self.writer.write(script)
        package = result.package
        if privacy is not None:
            package.metadata.privacy_status = privacy
        if publish_at is not None:
            package.metadata.publish_at = publish_at
            # publishAt requires private at upload time.
            package.metadata.privacy_status = PrivacyStatus.private

        # 2. Persist thumbnail spec.
        thumb_dir = self.public_dir / "thumbnails"
        thumb_dir.mkdir(parents=True, exist_ok=True)
        spec_path = thumb_dir / f"{script.episode_id}.json"
        spec_path.write_text(
            json.dumps(package.thumbnail.model_dump(mode="json"), indent=2)
        )

        # 3. Render the thumbnail PNG.
        thumb_png = self.out_dir / f"{script.episode_id}-thumbnail.png"
        self.renderer.render_still(
            composition_id="Thumbnail",
            out_path=thumb_png,
            frame=0,
            props={"thumbnailId": script.episode_id},
            scale=thumbnail_scale,
        )

        upload_video_id: Optional[str] = None
        upload_watch_url: Optional[str] = None
        thumbnail_set = False

        # 4. Optional upload.
        if upload:
            if video_path is None:
                video_path = self.out_dir / f"{script.episode_id}.mp4"
            if not video_path.exists():
                raise RuntimeError(
                    f"Cannot upload — video not found: {video_path}. "
                    f"Run Agent 3 (production) first."
                )
            # Lazy import — google libs are heavy, only load if needed.
            from pipeline.agents.youtube_uploader import YouTubeUploader

            uploader = YouTubeUploader()
            up = uploader.upload(
                video_path=video_path,
                metadata=package.metadata,
                thumbnail_path=thumb_png,
            )
            upload_video_id = up.video_id
            upload_watch_url = up.watch_url
            thumbnail_set = up.thumbnail_set

        return PublishResult(
            package=package,
            thumbnail_png=thumb_png,
            thumbnail_spec_json=spec_path,
            video_path=video_path,
            video_id=upload_video_id,
            watch_url=upload_watch_url,
            thumbnail_set=thumbnail_set,
        )


# ---------- CLI ---------- #

def main() -> None:
    """Usage: python -m pipeline.agents.publisher <script.json>
              [--upload] [--privacy=private|unlisted|public]
              [--video=<path.mp4>] [--scale=N]
              [--schedule]                           pick the next Thu/Fri/Sat/Sun 14:00 local
              [--publish-at=2026-05-08T14:00:00]     manual override (local or with tz)
              [--qc] [--qc-frames=N]                 run quality check first; --qc-frames samples N frames"""
    load_dotenv(
        Path(__file__).resolve().parent.parent.parent / ".env", override=True
    )

    args = sys.argv[1:]
    if not args:
        print(
            "usage: python -m pipeline.agents.publisher <script.json> "
            "[--upload] [--privacy=private|unlisted|public] [--video=<path>] "
            "[--scale=N] [--schedule] [--publish-at=ISO8601] [--qc] [--qc-frames=N]",
            file=sys.stderr,
        )
        sys.exit(2)

    script_path = Path(args[0])
    upload = "--upload" in args
    schedule = "--schedule" in args
    run_qc = "--qc" in args
    privacy: Optional[PrivacyStatus] = None
    video_path: Optional[Path] = None
    scale: Optional[float] = None
    publish_at_iso: Optional[str] = None
    qc_frames = 0
    for a in args[1:]:
        if a.startswith("--privacy="):
            privacy = PrivacyStatus(a.split("=", 1)[1])
        elif a.startswith("--video="):
            video_path = Path(a.split("=", 1)[1])
        elif a.startswith("--scale="):
            scale = float(a.split("=", 1)[1])
        elif a.startswith("--publish-at="):
            publish_at_iso = a.split("=", 1)[1]
        elif a.startswith("--qc-frames="):
            qc_frames = int(a.split("=", 1)[1])

    script = EpisodeScript.model_validate_json(script_path.read_text())

    # 0. Optional QC gate before any Claude / upload spend.
    if run_qc:
        from pipeline.agents.quality_check import QualityCheckAgent
        qc = QualityCheckAgent().check(
            script, video_path=video_path, sample_frames=qc_frames
        )
        if not qc.passed:
            print(
                f"[publisher] QC FAILED ({len(qc.errors)} errors). Aborting.",
                file=sys.stderr,
            )
            for issue in qc.errors:
                print(f"  - {issue.code}: {issue.message}", file=sys.stderr)
            sys.exit(2)
        if qc.warnings:
            print(f"[publisher] QC passed with {len(qc.warnings)} warnings.",
                  file=sys.stderr)

    # Resolve a publish_at if scheduling.
    publish_at: Optional[datetime] = None
    schedule_rationale: Optional[str] = None
    if publish_at_iso:
        from pipeline.agents.scheduler import parse_iso8601_to_utc
        publish_at = parse_iso8601_to_utc(publish_at_iso)
        schedule_rationale = f"manual: {publish_at.isoformat()}"
    elif schedule:
        from pipeline.agents.scheduler import pick_publish_at
        slot = pick_publish_at()
        publish_at = slot.publish_at_utc
        schedule_rationale = slot.rationale

    agent = PublisherAgent()
    result = agent.publish(
        script,
        video_path=video_path,
        privacy=privacy,
        upload=upload,
        thumbnail_scale=scale,
        publish_at=publish_at,
    )

    out = {
        "episode_id": script.episode_id,
        "title": result.package.metadata.title,
        "tags": result.package.metadata.tags,
        "privacy": result.package.metadata.privacy_status.value,
        "publish_at": (
            result.package.metadata.publish_at.isoformat()
            if result.package.metadata.publish_at else None
        ),
        "schedule_rationale": schedule_rationale,
        "thumbnail_png": str(result.thumbnail_png),
        "thumbnail_spec": str(result.thumbnail_spec_json),
        "uploaded": bool(result.video_id),
        "watch_url": result.watch_url,
        "thumbnail_set": result.thumbnail_set,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
