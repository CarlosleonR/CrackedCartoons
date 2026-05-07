"""Quality Check + Scheduler offline tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline.agents.quality_check import QualityCheckAgent
from pipeline.agents.scheduler import (
    PREFERRED_DAYS,
    parse_iso8601_to_utc,
    pick_publish_at,
)
from pipeline.schemas import (
    DialogueLine,
    EpisodeScript,
    Scene,
    SceneType,
    Speaker,
)


def _toy_script() -> EpisodeScript:
    return EpisodeScript(
        episode_id="Ep99-Test",
        title="t", logline="l",
        total_frames=300,
        scenes=[
            Scene(id="a", type=SceneType.title_card, start_frame=0, duration_frames=100, description="...", props={}),
            Scene(id="b", type=SceneType.dialogue_exchange, start_frame=100, duration_frames=100, description="...", props={}),
            Scene(id="c", type=SceneType.outro, start_frame=200, duration_frames=100, description="...", props={}),
        ],
        voiceover=[
            DialogueLine(speaker=Speaker.rock, text="One.", start_frame=10,
                         estimated_duration_frames=20, scene_id="a"),
        ],
        thumbnail_concept="...",
    )


# ---------- Quality Check ---------- #

def test_qc_reports_missing_video(tmp_path: Path) -> None:
    qc = QualityCheckAgent(public_dir=tmp_path / "public", out_dir=tmp_path / "out")
    report = qc.check(_toy_script(), video_path=tmp_path / "no.mp4")
    assert report.passed is False
    assert any(i.code == "video_missing" for i in report.issues)


def test_qc_reports_missing_audio(tmp_path: Path) -> None:
    # Video exists but is bogus; we still expect the audio asset error.
    public_dir = tmp_path / "public"
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)
    fake_video = out_dir / "Ep99-Test.mp4"
    # Tiny file -> "video_too_small" error, but importantly we also flag audio.
    fake_video.write_bytes(b"\x00" * 100)

    qc = QualityCheckAgent(public_dir=public_dir, out_dir=out_dir)
    report = qc.check(_toy_script(), video_path=fake_video)
    codes = {i.code for i in report.issues}
    assert "video_too_small" in codes
    assert "vo_audio_missing" in codes
    assert report.audio_files_missing >= 1


# ---------- Scheduler ---------- #

def test_scheduler_picks_preferred_weekday() -> None:
    # A Monday at 09:00 UTC.
    monday = datetime(2026, 5, 4, 9, 0, tzinfo=timezone.utc)
    slot = pick_publish_at(now=monday, tz=timezone.utc)
    # Picked day must be in preferred set.
    local_dt = slot.publish_at_utc.astimezone(timezone.utc)
    assert local_dt.weekday() in PREFERRED_DAYS
    # Hour preserved.
    assert local_dt.hour == 14
    # At least 1 hour ahead.
    assert (local_dt - monday) >= timedelta(hours=1)


def test_scheduler_skips_when_too_close_to_target() -> None:
    # 13:30 on a Friday — too close to 14:00 (less than 1h lead). Should pick
    # Saturday or later.
    friday_1330 = datetime(2026, 5, 8, 13, 30, tzinfo=timezone.utc)
    slot = pick_publish_at(
        now=friday_1330, tz=timezone.utc, min_lead=timedelta(hours=1)
    )
    assert slot.publish_at_utc.date() != friday_1330.date()


def test_scheduler_iso_format() -> None:
    monday = datetime(2026, 5, 4, 9, 0, tzinfo=timezone.utc)
    slot = pick_publish_at(now=monday, tz=timezone.utc)
    s = slot.to_iso8601_z()
    assert s.endswith("Z")
    # YouTube-acceptable shape.
    assert "T" in s and len(s) >= 20


def test_parse_iso8601_to_utc_handles_z_and_offset() -> None:
    a = parse_iso8601_to_utc("2026-05-08T14:00:00Z")
    b = parse_iso8601_to_utc("2026-05-08T10:00:00-04:00")
    assert a == b
