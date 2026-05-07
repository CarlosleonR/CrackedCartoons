"""Episode log — the diversity memory the Writer reads from.

Each line in `pipeline/knowledge/episode_log.jsonl` records one episode's
character / comedy_format / punchline_format / setting. The Writer reads the
last N entries to enforce anti-repetition rules.

Stays in the same `pipeline/knowledge/` directory as the Analyst's
KnowledgeBase, but in a separate file so they're independently testable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from pipeline.schemas import (
    Character,
    ComedyFormat,
    EpisodeScript,
    PunchlineFormat,
)


DEFAULT_PATH = (
    Path(__file__).resolve().parent.parent.parent / "knowledge" / "episode_log.jsonl"
)


class EpisodeLogEntry(BaseModel):
    episode_id: str
    title: str
    character: Character
    comedy_format: ComedyFormat
    punchline_format: PunchlineFormat
    setting: str
    written_at: datetime


class EpisodeLog:
    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def all(self) -> List[EpisodeLogEntry]:
        out: List[EpisodeLogEntry] = []
        with self.path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(EpisodeLogEntry.model_validate_json(line))
                except Exception:
                    # Skip corrupt lines.
                    continue
        return out

    def last(self, n: int = 3) -> List[EpisodeLogEntry]:
        return self.all()[-n:]

    def append(self, entry: EpisodeLogEntry) -> None:
        # Idempotent on episode_id — re-running the writer on the same id
        # shouldn't double-log.
        existing = {e.episode_id for e in self.all()}
        if entry.episode_id in existing:
            return
        with self.path.open("a") as f:
            f.write(entry.model_dump_json() + "\n")

    @staticmethod
    def from_script(script: EpisodeScript) -> Optional[EpisodeLogEntry]:
        """Build a log entry from a finished script. Returns None if the
        script is missing the diversity fields (legacy v1 episodes)."""
        if not (script.character and script.comedy_format and script.punchline_format):
            return None
        # Setting is per-scene; sample the first scene's setting (the writer
        # is required to keep it consistent across an episode).
        first_setting = "auto"
        for s in script.scenes:
            if isinstance(s.props, dict) and s.props.get("setting"):
                first_setting = str(s.props["setting"])
                break
        return EpisodeLogEntry(
            episode_id=script.episode_id,
            title=script.title,
            character=script.character,
            comedy_format=script.comedy_format,
            punchline_format=script.punchline_format,
            setting=first_setting,
            written_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def render_for_writer(entries: List[EpisodeLogEntry]) -> str:
        """Format the last-N entries as a markdown block for the writer's
        user message. Empty string if no entries."""
        if not entries:
            return ""
        lines = ["## Recent episodes — DO NOT REPEAT THESE"]
        for e in entries:
            lines.append(
                f"- **{e.episode_id}** \"{e.title}\" — "
                f"character: `{e.character.value}`, "
                f"format: `{e.comedy_format.value}`, "
                f"punchline: `{e.punchline_format.value}`, "
                f"setting: `{e.setting}`"
            )
        lines.append("")
        lines.append(
            "Pick a different `character`, a different `comedy_format`, "
            "and a different `punchline_format` from these. If The Rock "
            "appeared in the last 2 entries, you MUST use a different character."
        )
        return "\n".join(lines)
