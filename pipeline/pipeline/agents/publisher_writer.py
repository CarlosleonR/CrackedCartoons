"""Claude-side of Agent 5: turn an EpisodeScript into a PublishPackage
(YouTube metadata + thumbnail spec). Same caching pattern as the writer agent.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from anthropic import Anthropic
from anthropic.types import Message

from pipeline.schemas import EpisodeScript, PublishPackage


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "publisher_system.md"
TOOL_NAME = "submit_publish_package"
DEFAULT_MODEL = "claude-sonnet-4-5"


@dataclass
class PublishPackageResult:
    package: PublishPackage
    raw_tool_input: Dict[str, Any]
    usage: Dict[str, int]
    model: str


class PublisherWriter:
    """Generates metadata + thumbnail spec from an EpisodeScript via Claude."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        prompt_path: Path = PROMPT_PATH,
    ) -> None:
        env_key = os.environ.get("ANTHROPIC_API_KEY") or None
        resolved = api_key or env_key
        if not resolved:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Add it to pipeline/.env or export it."
            )
        self.client = Anthropic(api_key=resolved)
        self.model = model or os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self.max_tokens = max_tokens
        self.system_prompt_text = prompt_path.read_text()
        self.tool_definition = {
            "name": TOOL_NAME,
            "description": (
                "Submit the final YouTube metadata and thumbnail spec. Call this "
                "exactly once with a complete PublishPackage. Do not respond with text."
            ),
            "input_schema": PublishPackage.model_json_schema(),
            "cache_control": {"type": "ephemeral"},
        }

    def write(self, script: EpisodeScript) -> PublishPackageResult:
        # Send a compact view of the script — enough for metadata, no need for
        # frame-level timing.
        compact = {
            "episode_id": script.episode_id,
            "title_seed": script.title,
            "logline": script.logline,
            "thumbnail_concept": script.thumbnail_concept,
            "scenes": [
                {"id": s.id, "type": s.type.value, "description": s.description}
                for s in script.scenes
            ],
            "voiceover_lines": [
                {"speaker": l.speaker.value, "text": l.text} for l in script.voiceover
            ],
        }
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": self.system_prompt_text,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[self.tool_definition],
            tool_choice={"type": "tool", "name": TOOL_NAME},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Produce YouTube metadata + thumbnail spec for this "
                        "Cracked Cartoons episode. Call submit_publish_package "
                        "with both. Match the title and headline conventions "
                        "in the system prompt exactly.\n\n"
                        f"EPISODE:\n{_to_pretty_json(compact)}"
                    ),
                }
            ],
        )
        return self._extract(msg)

    def _extract(self, msg: Message) -> PublishPackageResult:
        for block in msg.content:
            if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
                pkg = PublishPackage.model_validate(block.input)
                return PublishPackageResult(
                    package=pkg,
                    raw_tool_input=block.input,  # type: ignore[arg-type]
                    usage={
                        "input_tokens": msg.usage.input_tokens,
                        "output_tokens": msg.usage.output_tokens,
                        "cache_creation_input_tokens":
                            getattr(msg.usage, "cache_creation_input_tokens", 0) or 0,
                        "cache_read_input_tokens":
                            getattr(msg.usage, "cache_read_input_tokens", 0) or 0,
                    },
                    model=self.model,
                )
        raise RuntimeError(
            f"Model did not call {TOOL_NAME!r}. stop_reason={msg.stop_reason}"
        )


def _to_pretty_json(obj: Any) -> str:
    import json as _json
    return _json.dumps(obj, indent=2, ensure_ascii=False)
