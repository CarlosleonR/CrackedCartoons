"""Idea Scout offline tests — no network, no Claude."""
from __future__ import annotations

from pipeline.agents.sources import ManualSource
from pipeline.agents.sources.manual import BUILTIN_SEEDS
from pipeline.schemas import IdeaBatch, TrendItem


def test_manual_source_builtin_seeds() -> None:
    s = ManualSource()
    out = s.fetch(limit=3)
    assert len(out) == 3
    assert all(isinstance(i, TrendItem) for i in out)
    assert all(i.source.startswith("manual") for i in out)


def test_manual_source_custom_items() -> None:
    s = ManualSource(items=[
        {"title": "x", "summary": "y"},
        {"title": "z", "source": "manual:custom"},
    ])
    out = s.fetch()
    assert len(out) == 2
    assert out[1].source == "manual:custom"


def test_idea_batch_validates() -> None:
    from pipeline.schemas import Concept

    batch = IdeaBatch(
        sources_used=["manual:builtin"],
        raw_candidates_count=8,
        candidates=[
            Concept(
                topic="x", premise="y", conflict="z", punchline="w",
            ),
        ],
    )
    assert batch.candidates[0].runtime_seconds == 30
    assert batch.raw_candidates_count == 8


def test_builtin_seeds_have_titles() -> None:
    assert all("title" in s for s in BUILTIN_SEEDS)
    assert len(BUILTIN_SEEDS) >= 5
