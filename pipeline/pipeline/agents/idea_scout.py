"""Agent 1 — Idea Scout.

Pulls TrendItems from configured sources, hands them to Claude, and gets back
an IdeaBatch (top 3 Concepts) ready to feed into Agent 2.

Same caching pattern as the other Claude-using agents: stable system prompt
+ tool definition cached, dynamic input (the trend batch + recent-episode
context) goes in the user message.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from anthropic import Anthropic
from anthropic.types import Message
from dotenv import load_dotenv

from pipeline.agents.sources import (
    DEFAULT_SUBREDDITS,
    ManualSource,
    RedditSource,
    TrendSource,
)
from pipeline.schemas import IdeaBatch, TrendItem


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "idea_scout_system.md"
)
TOOL_NAME = "submit_idea_batch"
DEFAULT_MODEL = "claude-sonnet-4-5"


@dataclass
class IdeaScoutResult:
    batch: IdeaBatch
    raw_items: List[TrendItem]
    usage: Dict[str, int]
    model: str


@dataclass
class IdeaScoutAgent:
    sources: List[TrendSource] = field(default_factory=list)
    api_key: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 3072

    client: Anthropic = field(init=False)
    system_prompt_text: str = field(init=False)
    tool_definition: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        env_key = os.environ.get("ANTHROPIC_API_KEY") or None
        resolved = self.api_key or env_key
        if not resolved:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Add it to pipeline/.env or export it."
            )
        self.client = Anthropic(api_key=resolved)
        self.model = self.model or os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self.system_prompt_text = PROMPT_PATH.read_text()
        self.tool_definition = {
            "name": TOOL_NAME,
            "description": (
                "Submit the top episode candidates as an IdeaBatch. Call this "
                "exactly once with a complete object. Do not respond with text."
            ),
            "input_schema": IdeaBatch.model_json_schema(),
            "cache_control": {"type": "ephemeral"},
        }
        if not self.sources:
            self.sources = [RedditSource(), ManualSource()]

    # ---------- public API ---------- #

    def scout(
        self,
        *,
        per_source_limit: int = 20,
        recent_episode_titles: Sequence[str] = (),
        target_count: int = 3,
    ) -> IdeaScoutResult:
        items: List[TrendItem] = []
        sources_used: List[str] = []
        for src in self.sources:
            fetched = src.fetch(limit=per_source_limit)
            if fetched:
                sources_used.append(src.name)
                items.extend(fetched)
        if not items:
            raise RuntimeError(
                "No trend items fetched from any source. Check your network or "
                "fall back to ManualSource."
            )

        msg = self._call_claude(
            items=items,
            recent_episode_titles=list(recent_episode_titles),
            target_count=target_count,
        )
        batch = self._extract(msg, sources_used=sources_used, raw_count=len(items))
        return IdeaScoutResult(
            batch=batch,
            raw_items=items,
            usage={
                "input_tokens": msg.usage.input_tokens,
                "output_tokens": msg.usage.output_tokens,
                "cache_creation_input_tokens":
                    getattr(msg.usage, "cache_creation_input_tokens", 0) or 0,
                "cache_read_input_tokens":
                    getattr(msg.usage, "cache_read_input_tokens", 0) or 0,
            },
            model=self.model or DEFAULT_MODEL,
        )

    # ---------- internals ---------- #

    def _call_claude(
        self,
        *,
        items: List[TrendItem],
        recent_episode_titles: List[str],
        target_count: int,
    ) -> Message:
        # Compact the trend items so we don't burn input tokens on URLs
        # and timestamps the model doesn't need.
        compact = [
            {"source": t.source, "title": t.title, "summary": t.summary, "url": t.url}
            for t in items
        ]
        user_msg = (
            f"Here are {len(items)} raw signals from the internet. "
            f"Filter for things The Rock could have absurd opinions about, then "
            f"call submit_idea_batch with the top {target_count} concepts.\n\n"
        )
        if recent_episode_titles:
            user_msg += (
                "Episodes already shipped — do not duplicate themes:\n"
                + "\n".join(f"- {t}" for t in recent_episode_titles)
                + "\n\n"
            )
        user_msg += "TREND ITEMS:\n" + json.dumps(compact, indent=2, ensure_ascii=False)

        return self.client.messages.create(
            model=self.model or DEFAULT_MODEL,
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

    def _extract(
        self, msg: Message, *, sources_used: List[str], raw_count: int
    ) -> IdeaBatch:
        for block in msg.content:
            if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
                payload = dict(block.input)  # type: ignore[arg-type]
                # Backfill bookkeeping fields the model shouldn't have to set.
                payload["sources_used"] = sources_used
                payload["raw_candidates_count"] = raw_count
                return IdeaBatch.model_validate(payload)
        raise RuntimeError(
            f"Model did not call {TOOL_NAME!r}. stop_reason={msg.stop_reason}"
        )


# ---------- CLI ---------- #

def main() -> None:
    """Usage: python -m pipeline.agents.idea_scout
                  [--out=ideas.json] [--top=N] [--no-reddit] [--per-source=N]
                  [--recent='Ep01: ...; Ep02: ...']"""
    load_dotenv(
        Path(__file__).resolve().parent.parent.parent / ".env", override=True
    )

    args = sys.argv[1:]
    out_path: Optional[Path] = None
    top = 3
    per_source = 15
    recent: List[str] = []
    use_reddit = True

    for a in args:
        if a.startswith("--out="):
            out_path = Path(a.split("=", 1)[1])
        elif a.startswith("--top="):
            top = int(a.split("=", 1)[1])
        elif a.startswith("--per-source="):
            per_source = int(a.split("=", 1)[1])
        elif a.startswith("--recent="):
            recent = [s.strip() for s in a.split("=", 1)[1].split(";") if s.strip()]
        elif a == "--no-reddit":
            use_reddit = False

    sources: List[TrendSource] = []
    if use_reddit:
        sources.append(RedditSource(per_sub=4))
    sources.append(ManualSource())  # always include builtin seeds as a floor

    agent = IdeaScoutAgent(sources=sources)
    result = agent.scout(
        per_source_limit=per_source,
        recent_episode_titles=recent,
        target_count=top,
    )

    payload = result.batch.model_dump(mode="json")
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"wrote {out_path}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2))

    u = result.usage
    print(
        f"\n[idea_scout] sources={result.batch.sources_used}  "
        f"raw_items={result.batch.raw_candidates_count}  "
        f"candidates={len(result.batch.candidates)}  "
        f"in={u['input_tokens']}  out={u['output_tokens']}  "
        f"cache_create={u['cache_creation_input_tokens']}  "
        f"cache_read={u['cache_read_input_tokens']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
