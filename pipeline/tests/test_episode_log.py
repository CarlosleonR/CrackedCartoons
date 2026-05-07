"""Episode log offline tests — no API."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pipeline.agents.episode_log import EpisodeLog, EpisodeLogEntry
from pipeline.schemas import (
    Character,
    ComedyFormat,
    DialogueLine,
    EpisodeScript,
    PunchlineFormat,
    Scene,
    SceneType,
    Speaker,
)


def _entry(eid: str, char: Character, fmt: ComedyFormat, pf: PunchlineFormat, setting: str) -> EpisodeLogEntry:
    return EpisodeLogEntry(
        episode_id=eid, title=f"Title {eid}",
        character=char, comedy_format=fmt, punchline_format=pf, setting=setting,
        written_at=datetime.now(timezone.utc),
    )


def test_log_append_and_dedup(tmp_path: Path) -> None:
    log = EpisodeLog(path=tmp_path / "log.jsonl")
    log.append(_entry("Ep01-A", Character.the_rock, ComedyFormat.the_confident_expert,
                      PunchlineFormat.verbal, "picnic"))
    log.append(_entry("Ep01-A", Character.the_rock, ComedyFormat.the_escalation,
                      PunchlineFormat.visual, "park"))  # dup id; should be ignored
    log.append(_entry("Ep02-B", Character.the_rock, ComedyFormat.the_confident_expert,
                      PunchlineFormat.verbal, "airport"))
    all_entries = log.all()
    assert [e.episode_id for e in all_entries] == ["Ep01-A", "Ep02-B"]


def test_last_n(tmp_path: Path) -> None:
    log = EpisodeLog(path=tmp_path / "log.jsonl")
    for i, char in enumerate([Character.the_rock, Character.gerald, Character.dave_from_hr,
                              Character.the_duck]):
        log.append(_entry(f"Ep{i:02d}-X", char, ComedyFormat.the_confident_expert,
                          PunchlineFormat.verbal, "x"))
    last3 = log.last(3)
    assert len(last3) == 3
    assert [e.character for e in last3] == [Character.gerald, Character.dave_from_hr, Character.the_duck]


def test_render_for_writer(tmp_path: Path) -> None:
    entries = [
        _entry("Ep01-A", Character.the_rock, ComedyFormat.the_confident_expert,
               PunchlineFormat.verbal, "picnic"),
        _entry("Ep02-B", Character.the_rock, ComedyFormat.the_confident_expert,
               PunchlineFormat.verbal, "airport"),
    ]
    rendered = EpisodeLog.render_for_writer(entries)
    assert "the_rock" in rendered
    assert "the_confident_expert" in rendered
    assert "DO NOT REPEAT" in rendered
    assert "different character" in rendered  # the rock-2x rule


def test_from_script_extracts_setting() -> None:
    script = EpisodeScript(
        episode_id="Ep03-Tarmac",
        title="Test",
        logline="A test.",
        total_frames=300,
        character=Character.gerald,
        comedy_format=ComedyFormat.the_silent_witness,
        punchline_format=PunchlineFormat.silent,
        scenes=[
            Scene(id="a", type=SceneType.title_card, start_frame=0, duration_frames=80,
                  description="...", props={"setting": "tarmac"}),
            Scene(id="b", type=SceneType.visual_beat, start_frame=80, duration_frames=120,
                  description="...", props={"setting": "tarmac"}),
            Scene(id="c", type=SceneType.outro, start_frame=200, duration_frames=100,
                  description="...", props={"setting": "tarmac"}),
        ],
        thumbnail_concept="...",
    )
    entry = EpisodeLog.from_script(script)
    assert entry is not None
    assert entry.character == Character.gerald
    assert entry.setting == "tarmac"


def test_from_script_skips_legacy() -> None:
    """A v1 script (no character/comedy_format) returns None — won't pollute the log."""
    script = EpisodeScript(
        episode_id="Ep00-Legacy",
        title="legacy", logline="legacy.",
        total_frames=300,
        scenes=[
            Scene(id="a", type=SceneType.title_card, start_frame=0, duration_frames=80,
                  description="...", props={}),
            Scene(id="b", type=SceneType.dialogue_exchange, start_frame=80, duration_frames=120,
                  description="...", props={}),
            Scene(id="c", type=SceneType.outro, start_frame=200, duration_frames=100,
                  description="...", props={}),
        ],
        thumbnail_concept="...",
    )
    assert EpisodeLog.from_script(script) is None
