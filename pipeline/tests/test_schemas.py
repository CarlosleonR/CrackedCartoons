"""Schema validation tests — no API calls, run before any cloud spend."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from pipeline.schemas import (
    Concept,
    DialogueLine,
    EpisodeScript,
    Scene,
    SceneType,
    SFXCue,
    Speaker,
)


def _scene(id: str, start: int, dur: int, type_: SceneType = SceneType.title_card) -> Scene:
    return Scene(
        id=id,
        type=type_,
        start_frame=start,
        duration_frames=dur,
        description="...",
        props={},
    )


def test_concept_minimal_roundtrips() -> None:
    c = Concept(
        topic="x",
        premise="y",
        conflict="z",
        punchline="w",
    )
    assert c.runtime_seconds == 30
    assert c.model_dump_json()


def test_episode_script_contiguous_scenes_pass() -> None:
    script = EpisodeScript(
        episode_id="Ep02-Test",
        title="Test",
        logline="A test.",
        total_frames=300,
        scenes=[
            _scene("a", 0, 100),
            _scene("b", 100, 100),
            _scene("c", 200, 100),
        ],
        thumbnail_concept="...",
    )
    assert script.total_frames == 300


def test_episode_script_gap_rejected() -> None:
    with pytest.raises(ValidationError) as ei:
        EpisodeScript(
            episode_id="Ep02-Test",
            title="Test",
            logline="A test.",
            total_frames=300,
            scenes=[
                _scene("a", 0, 100),
                _scene("b", 110, 100),  # gap of 10
                _scene("c", 210, 100),
            ],
            thumbnail_concept="...",
        )
    assert "expected 100" in str(ei.value)


def test_episode_script_total_frames_mismatch_rejected() -> None:
    with pytest.raises(ValidationError):
        EpisodeScript(
            episode_id="Ep02-Test",
            title="Test",
            logline="A test.",
            total_frames=500,  # claims 500, scenes sum to 300
            scenes=[
                _scene("a", 0, 100),
                _scene("b", 100, 100),
                _scene("c", 200, 100),
            ],
            thumbnail_concept="...",
        )


def test_voiceover_must_reference_real_scene() -> None:
    with pytest.raises(ValidationError):
        EpisodeScript(
            episode_id="Ep02-Test",
            title="Test",
            logline="A test.",
            total_frames=300,
            scenes=[_scene("a", 0, 300)],
            voiceover=[
                DialogueLine(
                    speaker=Speaker.rock,
                    text="hi",
                    start_frame=10,
                    estimated_duration_frames=20,
                    scene_id="ghost",
                )
            ],
            thumbnail_concept="...",
        )


def test_sfx_after_episode_end_rejected() -> None:
    with pytest.raises(ValidationError):
        EpisodeScript(
            episode_id="Ep02-Test",
            title="Test",
            logline="A test.",
            total_frames=300,
            scenes=[_scene("a", 0, 300)],
            sfx=[
                SFXCue(
                    description="boom",
                    start_frame=400,
                    duration_seconds=1.0,
                    scene_id="a",
                )
            ],
            thumbnail_concept="...",
        )


def test_episode_id_pattern_enforced() -> None:
    with pytest.raises(ValidationError):
        EpisodeScript(
            episode_id="bad id",
            title="Test",
            logline="A test.",
            total_frames=300,
            scenes=[_scene("a", 0, 300)],
            thumbnail_concept="...",
        )
