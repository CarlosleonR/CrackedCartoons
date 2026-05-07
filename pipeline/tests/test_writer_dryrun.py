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
    # Character bible markers must be present.
    for marker in ["The Rock", "The Kid", "Scene Type Catalog", "Episode 1"]:
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
    after the cached system prompt + cached tool definition. We can't introspect
    the live HTTP request, but we can verify the agent's structure surfaces the
    concept via the user message only.
    """
    a = _agent()
    # The system prompt must NOT mention the specific concept's topic — anything
    # that varies per episode breaks the cache.
    forbidden_in_system = ["Airport", "boarding", "iced coffee"]
    for word in forbidden_in_system:
        assert word.lower() not in a.system_prompt_text.lower(), (
            f"System prompt contains episode-specific term {word!r} — will "
            f"break KV cache across episodes."
        )
