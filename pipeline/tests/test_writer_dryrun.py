"""Verifies the writer's prep work without making an API call.

Run with: pytest tests/test_writer_dryrun.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.agents.writer import TOOL_NAME, WriterAgent
from pipeline.schemas import Concept


def _agent() -> WriterAgent:
    # No real key needed; we never call .write(). Anthropic SDK accepts a
    # placeholder key at construction time and only validates on request.
    return WriterAgent(api_key="sk-ant-test-not-used")


def test_system_prompt_loads_and_is_substantial() -> None:
    a = _agent()
    # Caching threshold for Sonnet is ~1024 tokens. Our prompt is well over.
    assert len(a.system_prompt_text) > 3000
    # Character bible + format library markers — the things that drive variety.
    for marker in [
        "The Rock", "Gerald", "Dave from HR", "The Duck",
        "Comedy Format Library",
        "FORMAT 1: The Confident Expert",
        "what_to_avoid_next_episode",
    ]:
        assert marker in a.system_prompt_text, f"missing {marker!r}"


def test_tool_definition_shape() -> None:
    a = _agent()
    td = a.tool_definition
    assert td["name"] == TOOL_NAME
    assert td["cache_control"] == {"type": "ephemeral"}
    schema = td["input_schema"]
    assert schema["type"] == "object"
    # Required fields must include the timing-critical ones.
    required = set(schema.get("required", []))
    for field in ("episode_id", "title", "total_frames", "scenes", "thumbnail_concept"):
        assert field in required, f"{field} should be required"


def test_example_concepts_validate() -> None:
    examples_dir = Path(__file__).resolve().parent.parent / "examples"
    for path in sorted(examples_dir.glob("concept_*.json")):
        c = Concept.model_validate_json(path.read_text())
        assert c.runtime_seconds in range(15, 61)
        assert c.premise and c.conflict and c.punchline


def test_user_message_is_kv_cache_friendly() -> None:
    """The dynamic content (the concept) must be the LAST thing in the request,
    after the cached system prompt + cached tool definition. Generic vocabulary
    (like the names of registered scene settings) is allowed; what we forbid is
    leaks of specific *episode content* — premises, punchlines, taglines from a
    real concept that would change per episode and bust the cache.
    """
    a = _agent()
    forbidden_in_system = [
        "Group Four",          # Ep2 punchline phrase
        "Zone Eleven",         # Ep2 punchline phrase
        "Iced Coffee",         # generic-but-pretend-episode example
    ]
    for phrase in forbidden_in_system:
        assert phrase.lower() not in a.system_prompt_text.lower(), (
            f"System prompt contains episode-specific phrase {phrase!r} — "
            f"will break KV cache across episodes."
        )
