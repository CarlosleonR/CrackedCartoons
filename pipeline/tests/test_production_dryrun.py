"""Production agent dry-run — no ElevenLabs calls, no Remotion renders.

Verifies the file-naming logic, dedup of SFX via reuse_key, and the
script.json layout that the generic composition consumes.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pipeline.agents.production import ProductionAgent, _line_basename, _sfx_basename, _slug
from pipeline.schemas import (
    DialogueLine,
    EpisodeScript,
    Scene,
    SceneType,
    SFXCue,
    Speaker,
)


def _toy_script() -> EpisodeScript:
    return EpisodeScript(
        episode_id="Ep99-Test",
        title="Test",
        logline="A test.",
        total_frames=300,
        scenes=[
            Scene(id="a", type=SceneType.title_card, start_frame=0, duration_frames=100,
                  description="...", props={}),
            Scene(id="b", type=SceneType.rating_beat, start_frame=100, duration_frames=100,
                  description="...", props={}),
            Scene(id="c", type=SceneType.rating_beat, start_frame=200, duration_frames=100,
                  description="...", props={}),
        ],
        voiceover=[
            DialogueLine(speaker=Speaker.rock, text="One.", start_frame=10,
                         estimated_duration_frames=20, scene_id="a"),
            DialogueLine(speaker=Speaker.kid, text="Two!", start_frame=110,
                         estimated_duration_frames=20, scene_id="b"),
        ],
        sfx=[
            SFXCue(description="ding", start_frame=120, duration_seconds=1.0, scene_id="b",
                   reuse_key="stamp_ding"),
            SFXCue(description="ding", start_frame=220, duration_seconds=1.0, scene_id="c",
                   reuse_key="stamp_ding"),  # same reuse_key as above
            SFXCue(description="trombone", start_frame=290, duration_seconds=2.0, scene_id="c"),
        ],
        thumbnail_concept="...",
    )


def test_slug_normalizes() -> None:
    assert _slug("Hey! That's MY sandwich!") == "hey_that_s_my_sandwich"
    assert _slug("") == "x"
    assert len(_slug("a" * 100)) == 28


def test_basenames_deterministic() -> None:
    line = DialogueLine(speaker=Speaker.rock, text="Disgrace.", start_frame=10,
                        estimated_duration_frames=20, scene_id="a")
    assert _line_basename(line, 3) == "03_rock_disgrace.mp3"

    cue_with_key = SFXCue(description="ding", start_frame=10, duration_seconds=1.0,
                          scene_id="a", reuse_key="stamp_ding")
    assert _sfx_basename(cue_with_key, 5) == "stamp_ding.mp3"

    cue_no_key = SFXCue(description="weird sproing", start_frame=10, duration_seconds=1.0,
                        scene_id="a")
    name = _sfx_basename(cue_no_key, 0)
    assert name.startswith("00_weird_sproing_")
    assert name.endswith(".mp3")


def test_production_dedup_and_layout(tmp_path: Path) -> None:
    public_dir = tmp_path / "public"
    out_dir = tmp_path / "out"
    public_dir.mkdir()

    eleven = MagicMock()
    # Make the mock create the file the agent expects to exist on disk.
    def fake_speech(*, out_path: Path, **kw):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 10000)  # bogus mp3
        return out_path
    def fake_sfx(*, out_path: Path, **kw):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 10000)
        return out_path
    eleven.synthesize_speech.side_effect = fake_speech
    eleven.synthesize_sfx.side_effect = fake_sfx

    renderer = MagicMock()
    agent = ProductionAgent(
        public_dir=public_dir,
        out_dir=out_dir,
        elevenlabs=eleven,
        renderer=renderer,
    )

    script = _toy_script()
    result = agent.produce(script, skip_render=True)

    # Two VO lines -> two TTS calls.
    assert eleven.synthesize_speech.call_count == 2
    # Three SFX cues but two share reuse_key="stamp_ding" -> only 2 unique calls.
    assert eleven.synthesize_sfx.call_count == 2

    # script.json exists at the right place.
    sj = public_dir / "scripts" / f"{script.episode_id}.json"
    assert sj.exists()

    # audio_src fields are populated and relative to public/.
    import json
    payload = json.loads(sj.read_text())
    assert all("audio_src" in vo for vo in payload["voiceover"])
    assert all("audio_src" in cue for cue in payload["sfx"])
    # The two stamp_ding cues should resolve to the same file.
    stamp_paths = [c["audio_src"] for c in payload["sfx"] if c.get("reuse_key") == "stamp_ding"]
    assert len(set(stamp_paths)) == 1

    # No render call (skip_render=True).
    renderer.render.assert_not_called()
