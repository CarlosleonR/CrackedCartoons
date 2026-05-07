"""Agent 2 — Writer.

Takes a `Concept` (from Agent 1, Idea Scout) and produces an `EpisodeScript`
(consumed by Agent 3, Production).

Design notes
------------
* Structured output is enforced via Anthropic **tool use**, not regex on a
  free-form response. We register a single tool whose `input_schema` is the
  Pydantic JSON schema for `EpisodeScript`, then `tool_choice` forces the model
  to call it. Whatever it passes is what we get — Pydantic re-validates after.

* Prompt caching keeps cost flat as the pipeline scales. The system prompt and
  the tool definition are large and stable; both get `cache_control: ephemeral`.
  Only the user message (the concept itself) varies per episode, so each new
  run hits the cache for ~all the static tokens.

* No CrewAI dependency yet. The class exposes a plain `write(concept) -> script`
  method that a CrewAI `Tool` or `Task` can wrap when we get to orchestration.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from anthropic import Anthropic
from anthropic.types import Message
from dotenv import load_dotenv

from pipeline.schemas import Concept, EpisodeScript


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "writer_system.md"
TOOL_NAME = "submit_episode_script"
DEFAULT_MODEL = "claude-sonnet-4-5"


@dataclass
class WriterResult:
    script: EpisodeScript
    raw_tool_input: Dict[str, Any]
    usage: Dict[str, int]
    model: str


class WriterAgent:
    """Stateless writer. Construct once, call `write(concept)` many times."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        prompt_path: Path = PROMPT_PATH,
    ) -> None:
        # Treat empty-string env vars as missing — a common foot-gun.
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
        self.tool_definition = self._build_tool_definition()

    # ---------- public API ---------- #

    def write(self, concept: Concept) -> WriterResult:
        message = self._call_claude(concept)
        tool_input = self._extract_tool_input(message)
        script = EpisodeScript.model_validate(tool_input)
        # Diversity log — append the new episode so the next writer call
        # avoids repeating it. Skip silently if the script is missing the
        # diversity fields (legacy).
        try:
            from pipeline.agents.episode_log import EpisodeLog
            entry = EpisodeLog.from_script(script)
            if entry is not None:
                EpisodeLog().append(entry)
        except Exception:
            pass

        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "cache_creation_input_tokens": getattr(
                message.usage, "cache_creation_input_tokens", 0
            ) or 0,
            "cache_read_input_tokens": getattr(
                message.usage, "cache_read_input_tokens", 0
            ) or 0,
        }
        return WriterResult(
            script=script,
            raw_tool_input=tool_input,
            usage=usage,
            model=self.model,
        )

    # ---------- internals ---------- #

    def _build_tool_definition(self) -> Dict[str, Any]:
        """Pydantic → JSON Schema → Anthropic tool definition.

        The Anthropic API accepts standard JSON Schema with a few caveats:
        - Top-level type must be `object`.
        - `$defs` / `$ref` are supported and used for our nested types.
        """
        schema = EpisodeScript.model_json_schema()
        return {
            "name": TOOL_NAME,
            "description": (
                "Submit the final structured episode script. Call this exactly "
                "once with a complete EpisodeScript. Do not respond with text."
            ),
            "input_schema": schema,
            # cache_control on the LAST tool definition caches all preceding
            # tool blocks plus the system prompt prefix. With one tool, that's
            # this one.
            "cache_control": {"type": "ephemeral"},
        }

    def _call_claude(self, concept: Concept) -> Message:
        # Append two stable user-message addenda (NOT system prompt — caching).
        #
        # 1. Recent episode log (last 3) so the writer enforces anti-repetition.
        # 2. Accumulated KnowledgeNotes from Agent 6.
        recent_block = ""
        try:
            from pipeline.agents.episode_log import EpisodeLog
            recent_block = EpisodeLog.render_for_writer(EpisodeLog().last(3))
        except Exception:
            recent_block = ""

        lessons_block = ""
        try:
            from pipeline.agents.knowledge_base import KnowledgeBase
            lessons_block = KnowledgeBase().render_for_writer()
        except Exception:
            lessons_block = ""

        user_msg = (
            "Write the next episode of Cracked Cartoons from this concept. "
            "Call the submit_episode_script tool with the complete "
            "EpisodeScript. Stay disciplined on timing — scene durations "
            "must sum to total_frames; voiceover and SFX start_frames "
            "must reference real scene ids and stay within the episode.\n\n"
            f"CONCEPT:\n{concept.model_dump_json(indent=2)}"
        )
        if recent_block:
            user_msg += "\n\n" + recent_block
        if lessons_block:
            user_msg += "\n\n" + lessons_block

        return self.client.messages.create(
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
            messages=[{"role": "user", "content": user_msg}],
        )

    def _extract_tool_input(self, message: Message) -> Dict[str, Any]:
        for block in message.content:
            if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
                return block.input  # type: ignore[return-value]
        raise RuntimeError(
            f"Model did not call {TOOL_NAME!r}. stop_reason={message.stop_reason}, "
            f"content_types={[getattr(b, 'type', '?') for b in message.content]}"
        )


# ---------- CLI ---------- #

def main() -> None:
    """Usage: python -m pipeline.agents.writer <concept.json> [out.json]"""
    # override=True so .env wins over an empty/stale value in the shell env.
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

    if len(sys.argv) < 2:
        print(
            "usage: python -m pipeline.agents.writer <concept.json> [out.json]",
            file=sys.stderr,
        )
        sys.exit(2)

    concept_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else None

    concept = Concept.model_validate_json(concept_path.read_text())
    agent = WriterAgent()
    result = agent.write(concept)

    payload = result.script.model_dump(mode="json")
    if out_path:
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"wrote {out_path}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2))

    u = result.usage
    print(
        f"\n[writer] model={result.model}  in={u['input_tokens']}  out={u['output_tokens']}  "
        f"cache_create={u['cache_creation_input_tokens']}  "
        f"cache_read={u['cache_read_input_tokens']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
