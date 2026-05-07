"""Agent 6 — Analyst.

Pipeline:
  episode_id (and optional video_id)
    -> fetch metrics + comments via YouTubeAnalyticsClient
    -> hand to Claude with the original EpisodeScript for context
    -> Claude returns AnalystOutput { report, new_knowledge[] }
    -> persist new_knowledge to KnowledgeBase JSONL
    -> return the report and how many notes were added.

The KnowledgeBase is then read by Agent 2 (Writer) on subsequent runs.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from anthropic.types import Message
from dotenv import load_dotenv

from pipeline.agents.knowledge_base import KnowledgeBase
from pipeline.agents.youtube_analytics import (
    YouTubeAnalyticsClient,
    YouTubeAnalyticsError,
)
from pipeline.schemas import (
    AnalystOutput,
    EpisodeScript,
    VideoMetrics,
)


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "analyst_system.md"
)
TOOL_NAME = "submit_analyst_output"
DEFAULT_MODEL = "claude-sonnet-4-5"


@dataclass
class AnalystResult:
    output: AnalystOutput
    knowledge_notes_added: int
    usage: Dict[str, int]
    model: str


@dataclass
class AnalystAgent:
    api_key: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 3072
    knowledge_base: Optional[KnowledgeBase] = None
    youtube: Optional[YouTubeAnalyticsClient] = None

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
                "Submit the analyst's report and any durable knowledge notes. "
                "Call this exactly once. Do not respond with text."
            ),
            "input_schema": AnalystOutput.model_json_schema(),
            "cache_control": {"type": "ephemeral"},
        }
        self.knowledge_base = self.knowledge_base or KnowledgeBase()

    # ---------- public API ---------- #

    def analyze(
        self,
        *,
        script: EpisodeScript,
        video_id: str,
        comment_limit: int = 25,
        manual_metrics: Optional[VideoMetrics] = None,
    ) -> AnalystResult:
        # 1. Fetch live data (or use provided manual metrics, useful for tests).
        if manual_metrics is None:
            try:
                youtube = self.youtube or YouTubeAnalyticsClient()
                metrics = youtube.fetch_metrics(video_id=video_id)
                comments = youtube.fetch_top_comments(
                    video_id=video_id, limit=comment_limit
                )
            except YouTubeAnalyticsError as e:
                raise RuntimeError(f"YouTube fetch failed: {e}")
        else:
            metrics = manual_metrics
            comments = []

        # 2. Hand context to Claude.
        msg = self._call_claude(
            script=script,
            metrics=metrics,
            comments=comments,
            existing_notes=self.knowledge_base.all_notes(),  # type: ignore[union-attr]
        )
        output = self._extract(
            msg,
            script_episode_id=script.episode_id,
            script_title=script.title,
            metrics=metrics,
            comments=comments,
            video_id=video_id,
        )

        # 3. Persist new knowledge (append-only, dedup by id).
        n_added = self.knowledge_base.append_many(output.new_knowledge)  # type: ignore[union-attr]

        return AnalystResult(
            output=output,
            knowledge_notes_added=n_added,
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
        self, *, script, metrics, comments, existing_notes
    ) -> Message:
        compact = {
            "episode_id": script.episode_id,
            "title": script.title,
            "logline": script.logline,
            "voiceover_lines": [
                {"speaker": l.speaker.value, "text": l.text}
                for l in script.voiceover
            ],
            "scenes": [
                {"id": s.id, "type": s.type.value, "duration_frames": s.duration_frames}
                for s in script.scenes
            ],
            "metrics": metrics.model_dump(mode="json"),
            "top_comments": [c.model_dump(mode="json") for c in comments],
            "existing_knowledge_ids": [n.id for n in existing_notes],
        }
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
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Read this episode's performance. Produce an "
                        "EpisodeReport and any durable KnowledgeNotes. "
                        "Skip note-creation if nothing here will repeat.\n\n"
                        f"DATA:\n{json.dumps(compact, indent=2, ensure_ascii=False)}"
                    ),
                }
            ],
        )

    def _extract(
        self,
        msg: Message,
        *,
        script_episode_id: str,
        script_title: str,
        metrics,
        comments,
        video_id: str,
    ) -> AnalystOutput:
        for block in msg.content:
            if getattr(block, "type", None) == "tool_use" and block.name == TOOL_NAME:
                payload = dict(block.input)  # type: ignore[arg-type]
                # Backfill bookkeeping the model shouldn't have to set.
                report = payload.setdefault("report", {})
                report.setdefault("episode_id", script_episode_id)
                report.setdefault("video_id", video_id)
                report.setdefault("title", script_title)
                report.setdefault("metrics", metrics.model_dump(mode="json"))
                report.setdefault(
                    "top_comments", [c.model_dump(mode="json") for c in comments]
                )
                return AnalystOutput.model_validate(payload)
        raise RuntimeError(
            f"Model did not call {TOOL_NAME!r}. stop_reason={msg.stop_reason}"
        )


# ---------- CLI ---------- #

def main() -> None:
    """Usage: python -m pipeline.agents.analyst <script.json> --video=<youtube_id>
              [--out=report.json]"""
    load_dotenv(
        Path(__file__).resolve().parent.parent.parent / ".env", override=True
    )

    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print(
            "usage: python -m pipeline.agents.analyst <script.json> "
            "--video=<youtube_id> [--out=report.json]",
            file=sys.stderr,
        )
        sys.exit(2)

    script_path = Path(args[0])
    video_id: Optional[str] = None
    out_path: Optional[Path] = None
    for a in args[1:]:
        if a.startswith("--video="):
            video_id = a.split("=", 1)[1]
        elif a.startswith("--out="):
            out_path = Path(a.split("=", 1)[1])
    if not video_id:
        sys.exit("--video=<youtube_id> is required")

    script = EpisodeScript.model_validate_json(script_path.read_text())
    agent = AnalystAgent()
    result = agent.analyze(script=script, video_id=video_id)

    payload = result.output.model_dump(mode="json")
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"wrote {out_path}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2))

    u = result.usage
    print(
        f"\n[analyst] knowledge_notes_added={result.knowledge_notes_added}  "
        f"in={u['input_tokens']}  out={u['output_tokens']}  "
        f"cache_create={u['cache_creation_input_tokens']}  "
        f"cache_read={u['cache_read_input_tokens']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
