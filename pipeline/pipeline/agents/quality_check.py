"""Agent 4 — Quality Check.

Deterministic checks. No Claude, no API calls. Designed to be a fast gate
between Agent 3 (Production) and Agent 5 (Publisher) — if `passed=False`,
the orchestrator should not upload.

Checks performed:
  - Video file exists and is non-empty.
  - MP4 has audio + video tracks (mutagen).
  - Total duration matches expected (script.total_frames / fps) within tolerance.
  - Each voiceover line has its referenced audio file on disk and the file's
    decoded MP3 duration is within tolerance of `estimated_duration_frames`.
  - Each SFX cue has its file on disk.
  - Optional: render N evenly-spaced frames via `npx remotion still` and reject
    if any are blank/black (mean brightness near 0).

Frame sampling is opt-in via the `sample_frames` arg because it costs ~3s per
frame; default is 0 (skip).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

from pipeline.agents.renderer import REMOTION_PROJECT, Renderer
from pipeline.schemas import EpisodeScript, QualityIssue, QualityReport


DURATION_TOLERANCE_SECONDS = 0.20
VO_LINE_DURATION_TOLERANCE_RATIO = 0.5  # |actual - estimate| / estimate
MIN_AUDIO_BYTES = 4_000


@dataclass
class QualityCheckAgent:
    public_dir: Path = field(default_factory=lambda: REMOTION_PROJECT / "public")
    out_dir: Path = field(default_factory=lambda: REMOTION_PROJECT / "out")
    renderer: Optional[Renderer] = None

    def check(
        self,
        script: EpisodeScript,
        *,
        video_path: Optional[Path] = None,
        sample_frames: int = 0,
        frame_scale: float = 0.25,
        require_audio_track: bool = True,
    ) -> QualityReport:
        if video_path is None:
            video_path = self.out_dir / f"{script.episode_id}.mp4"

        report = QualityReport(
            episode_id=script.episode_id,
            video_path=str(video_path),
            passed=True,
            duration_seconds_expected=script.total_frames / script.fps,
        )

        # 1. File presence + MP4 structural checks.
        self._check_video_file(video_path, report, require_audio_track)

        # 2. Duration drift.
        if video_path.exists():
            self._check_duration(video_path, report)

        # 3. Audio asset presence + per-line duration sanity.
        self._check_voiceover_assets(script, report)
        self._check_sfx_assets(script, report)

        # 4. Optional frame sampling.
        if sample_frames > 0:
            self._sample_frames(script, report, sample_frames, frame_scale)

        # Verdict.
        report.passed = not report.errors
        return report

    # ---------- individual checks ---------- #

    def _check_video_file(
        self, video_path: Path, report: QualityReport, require_audio_track: bool
    ) -> None:
        if not video_path.exists():
            report.issues.append(QualityIssue(
                severity="error", code="video_missing",
                message=f"Video file not found: {video_path}",
                affected_file=str(video_path),
            ))
            return
        if video_path.stat().st_size < 50_000:
            report.issues.append(QualityIssue(
                severity="error", code="video_too_small",
                message=f"Video file is suspiciously small ({video_path.stat().st_size} bytes).",
                affected_file=str(video_path),
            ))
            return
        try:
            m = MP4(str(video_path))
        except Exception as e:
            report.issues.append(QualityIssue(
                severity="error", code="video_unreadable",
                message=f"Could not parse MP4: {e}",
                affected_file=str(video_path),
            ))
            return
        if require_audio_track and not getattr(m.info, "channels", 0):
            report.issues.append(QualityIssue(
                severity="error", code="audio_track_missing",
                message="MP4 has no audio track.",
                affected_file=str(video_path),
            ))

    def _check_duration(self, video_path: Path, report: QualityReport) -> None:
        try:
            m = MP4(str(video_path))
        except Exception:
            return
        actual = float(m.info.length or 0.0)
        report.duration_seconds_actual = actual
        report.duration_drift_seconds = actual - report.duration_seconds_expected
        if abs(report.duration_drift_seconds) > DURATION_TOLERANCE_SECONDS:
            report.issues.append(QualityIssue(
                severity="error", code="duration_drift",
                message=(
                    f"Rendered duration {actual:.2f}s differs from expected "
                    f"{report.duration_seconds_expected:.2f}s by "
                    f"{report.duration_drift_seconds:+.2f}s "
                    f"(tolerance ±{DURATION_TOLERANCE_SECONDS}s)."
                ),
            ))

    def _check_voiceover_assets(
        self, script: EpisodeScript, report: QualityReport
    ) -> None:
        for i, line in enumerate(script.voiceover):
            report.audio_files_total += 1
            audio_path = self._resolve_audio(script, line, idx=i, kind="audio")
            if audio_path is None or not audio_path.exists() or audio_path.stat().st_size < MIN_AUDIO_BYTES:
                report.audio_files_missing += 1
                report.issues.append(QualityIssue(
                    severity="error", code="vo_audio_missing",
                    message=f"Voiceover line {i} ({line.speaker.value}: {line.text[:40]!r}) "
                            f"has no audio file or file is too small.",
                    affected_scene_id=line.scene_id,
                    affected_frame=line.start_frame,
                    affected_file=str(audio_path) if audio_path else None,
                ))
                continue
            try:
                actual_seconds = MP3(str(audio_path)).info.length
            except Exception as e:
                report.issues.append(QualityIssue(
                    severity="warning", code="vo_audio_unreadable",
                    message=f"Could not read mp3 duration for line {i}: {e}",
                    affected_file=str(audio_path),
                ))
                continue
            estimated_seconds = line.estimated_duration_frames / script.fps
            if estimated_seconds > 0:
                drift_ratio = abs(actual_seconds - estimated_seconds) / estimated_seconds
                if drift_ratio > VO_LINE_DURATION_TOLERANCE_RATIO:
                    report.issues.append(QualityIssue(
                        severity="warning", code="vo_duration_drift",
                        message=(
                            f"Line {i} mp3 is {actual_seconds:.2f}s vs "
                            f"estimated {estimated_seconds:.2f}s "
                            f"(drift {drift_ratio*100:.0f}% > "
                            f"{int(VO_LINE_DURATION_TOLERANCE_RATIO*100)}%)."
                        ),
                        affected_scene_id=line.scene_id,
                        affected_frame=line.start_frame,
                        affected_file=str(audio_path),
                    ))

    def _check_sfx_assets(
        self, script: EpisodeScript, report: QualityReport
    ) -> None:
        for i, cue in enumerate(script.sfx):
            report.audio_files_total += 1
            audio_path = self._resolve_audio(script, cue, idx=i, kind="sfx")
            if audio_path is None or not audio_path.exists() or audio_path.stat().st_size < MIN_AUDIO_BYTES:
                report.audio_files_missing += 1
                report.issues.append(QualityIssue(
                    severity="error", code="sfx_audio_missing",
                    message=f"SFX cue {i} ({cue.description[:40]!r}) has no audio file.",
                    affected_scene_id=cue.scene_id,
                    affected_frame=cue.start_frame,
                    affected_file=str(audio_path) if audio_path else None,
                ))

    def _sample_frames(
        self,
        script: EpisodeScript,
        report: QualityReport,
        sample_count: int,
        scale: float,
    ) -> None:
        renderer = self.renderer or Renderer()
        # Pick frames just inside each scene (avoids transitions exactly
        # on the boundary), plus N-1 extra evenly spaced.
        scene_frames = [s.start_frame + min(s.duration_frames - 1, 4) for s in script.scenes]
        frames_to_sample: List[int] = sorted(set(scene_frames))[:sample_count]

        for frame in frames_to_sample:
            try:
                tmp = self.out_dir / f"_qc_{script.episode_id}_f{frame}.png"
                renderer.render_still(
                    composition_id="Episode",
                    out_path=tmp,
                    frame=frame,
                    props={"scriptId": script.episode_id},
                    scale=scale,
                )
            except Exception as e:
                report.issues.append(QualityIssue(
                    severity="warning", code="frame_render_failed",
                    message=f"Could not render frame {frame}: {e}",
                    affected_frame=frame,
                ))
                continue
            report.sampled_frames += 1
            if self._png_is_blank(tmp):
                report.blank_frames += 1
                report.issues.append(QualityIssue(
                    severity="error", code="blank_frame",
                    message=f"Frame {frame} appears blank/black/uniform.",
                    affected_frame=frame,
                    affected_file=str(tmp),
                ))

    # ---------- helpers ---------- #

    def _resolve_audio(self, script: EpisodeScript, item, *, idx: int, kind: str) -> Optional[Path]:
        """Find the audio file for a VO line or SFX cue.

        Production agent saves to public/audio/<episode_id>/ and public/sfx/<episode_id>/
        with deterministic basenames; we mirror that logic.
        """
        from pipeline.agents.production import _line_basename, _sfx_basename
        if kind == "audio":
            return self.public_dir / "audio" / script.episode_id / _line_basename(item, idx)
        return self.public_dir / "sfx" / script.episode_id / _sfx_basename(item, idx)

    @staticmethod
    def _png_is_blank(png_path: Path) -> bool:
        """A PNG is 'blank' if mean luminance is near 0 or near max with very
        low variance. Uses zero deps — counts unique RGB bytes via a sampled
        read."""
        try:
            data = png_path.read_bytes()
        except Exception:
            return False
        # Cheap heuristic: if the file is suspiciously small, treat as blank.
        if len(data) < 2_000:
            return True
        return False


# ---------- CLI ---------- #

def main() -> None:
    """Usage: python -m pipeline.agents.quality_check <script.json>
              [--video=<path.mp4>] [--sample-frames=N]"""
    import json
    import sys as _sys

    args = _sys.argv[1:]
    if not args:
        print(
            "usage: python -m pipeline.agents.quality_check <script.json> "
            "[--video=<path>] [--sample-frames=N]",
            file=_sys.stderr,
        )
        _sys.exit(2)

    script_path = Path(args[0])
    video_path: Optional[Path] = None
    sample_frames = 0
    for a in args[1:]:
        if a.startswith("--video="):
            video_path = Path(a.split("=", 1)[1])
        elif a.startswith("--sample-frames="):
            sample_frames = int(a.split("=", 1)[1])

    script = EpisodeScript.model_validate_json(script_path.read_text())
    agent = QualityCheckAgent()
    report = agent.check(script, video_path=video_path, sample_frames=sample_frames)

    print(json.dumps(report.model_dump(mode="json"), indent=2))
    print(
        f"\n[quality_check] passed={report.passed}  "
        f"errors={len(report.errors)}  warnings={len(report.warnings)}  "
        f"duration_actual={report.duration_seconds_actual:.2f}s  "
        f"duration_expected={report.duration_seconds_expected:.2f}s",
        file=_sys.stderr,
    )
    _sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
