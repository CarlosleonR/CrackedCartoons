"""Analyst offline tests — no YouTube, no Anthropic.

Mocks the AnalystAgent's Anthropic client and exercises:
- the prep work (input schema, prompt loading)
- KnowledgeBase append / dedup / writer rendering
- end-to-end with manual_metrics (skips YouTube fetch)
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pipeline.agents.analyst import AnalystAgent, TOOL_NAME
from pipeline.agents.knowledge_base import KnowledgeBase
from pipeline.schemas import (
    AnalystOutput,
    CommentSample,
    DialogueLine,
    EpisodeReport,
    EpisodeScript,
    KnowledgeImpact,
    KnowledgeNote,
    Scene,
    SceneType,
    Sentiment,
    Speaker,
    VideoMetrics,
)


def _toy_script() -> EpisodeScript:
    return EpisodeScript(
        episode_id="Ep99-Test",
        title="Test Title",
        logline="A test.",
        total_frames=300,
        scenes=[
            Scene(id="a", type=SceneType.title_card, start_frame=0, duration_frames=80,
                  description="...", props={}),
            Scene(id="b", type=SceneType.dialogue_exchange, start_frame=80, duration_frames=120,
                  description="...", props={}),
            Scene(id="c", type=SceneType.outro, start_frame=200, duration_frames=100,
                  description="...", props={}),
        ],
        voiceover=[
            DialogueLine(speaker=Speaker.rock, text="One.", start_frame=10,
                         estimated_duration_frames=20, scene_id="a"),
        ],
        thumbnail_concept="...",
    )


def test_knowledge_base_append_dedup(tmp_path: Path) -> None:
    kb = KnowledgeBase(path=tmp_path / "notes.jsonl")
    n1 = KnowledgeNote(
        id="kn-2026-05-test-one",
        derived_from=["Ep99-Test"],
        finding="Lead with a verb in the title.",
        impacts=KnowledgeImpact.title,
        confidence="high",
    )
    n2 = KnowledgeNote(
        id="kn-2026-05-test-one",  # same id
        derived_from=["Ep99-Test"],
        finding="Different finding.",
        impacts=KnowledgeImpact.hook,
        confidence="medium",
    )
    kb.append(n1)
    kb.append(n2)  # should dedup

    notes = kb.all_notes()
    assert len(notes) == 1
    assert notes[0].finding.startswith("Lead")


def test_knowledge_base_render_for_writer(tmp_path: Path) -> None:
    kb = KnowledgeBase(path=tmp_path / "notes.jsonl")
    kb.append_many([
        KnowledgeNote(
            id="kn-x-1", derived_from=["E1"],
            finding="Open with the conflict, not the setup.",
            impacts=KnowledgeImpact.hook, confidence="high",
        ),
        KnowledgeNote(
            id="kn-x-2", derived_from=["E1"],
            finding="Titles with verbs in caps outperform noun-led titles.",
            impacts=KnowledgeImpact.title, confidence="medium",
        ),
        KnowledgeNote(
            id="kn-x-3", derived_from=["E1"],
            finding="Speculative thumbnail change.",
            impacts=KnowledgeImpact.thumbnail, confidence="low",
        ),
    ])
    rendered = kb.render_for_writer(min_confidence="medium")
    assert "Lessons learned" in rendered
    assert "hook" in rendered
    assert "title" in rendered
    # Low-confidence note must be excluded.
    assert "Speculative" not in rendered


def test_analyst_with_manual_metrics_persists_notes(tmp_path: Path) -> None:
    kb = KnowledgeBase(path=tmp_path / "notes.jsonl")

    fake_output_dict = AnalystOutput(
        report=EpisodeReport(
            episode_id="Ep99-Test",
            video_id="abc123",
            title="Test Title",
            metrics=VideoMetrics(video_id="abc123", views=10),
            top_comments=[],
            sentiment=Sentiment.neutral,
            what_worked=["Title was tight."],
            what_didnt=["Hook arrived at frame 90, too late."],
            suggestions_for_writer=["Move the conflict before frame 60."],
        ),
        new_knowledge=[
            KnowledgeNote(
                id="kn-2026-05-late-hook",
                derived_from=["Ep99-Test"],
                finding="If the hook lands after frame 60, retention drops sharply.",
                impacts=KnowledgeImpact.hook,
                confidence="medium",
            ),
        ],
    ).model_dump(mode="json")

    fake_block = MagicMock()
    fake_block.type = "tool_use"
    fake_block.name = TOOL_NAME
    fake_block.input = fake_output_dict

    fake_msg = MagicMock()
    fake_msg.content = [fake_block]
    fake_msg.stop_reason = "tool_use"
    fake_msg.usage.input_tokens = 100
    fake_msg.usage.output_tokens = 80
    fake_msg.usage.cache_creation_input_tokens = 0
    fake_msg.usage.cache_read_input_tokens = 0

    agent = AnalystAgent(api_key="sk-ant-fake", knowledge_base=kb)
    agent.client = MagicMock()
    agent.client.messages.create.return_value = fake_msg

    result = agent.analyze(
        script=_toy_script(),
        video_id="abc123",
        manual_metrics=VideoMetrics(video_id="abc123", views=10),
    )

    assert result.knowledge_notes_added == 1
    assert result.output.report.sentiment == Sentiment.neutral
    assert len(kb.all_notes()) == 1
    assert kb.all_notes()[0].id == "kn-2026-05-late-hook"

    # Re-running should not duplicate the note.
    agent.analyze(
        script=_toy_script(),
        video_id="abc123",
        manual_metrics=VideoMetrics(video_id="abc123", views=10),
    )
    assert len(kb.all_notes()) == 1
