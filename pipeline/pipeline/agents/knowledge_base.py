"""Append-only JSONL knowledge base of learnings produced by Agent 6.

Each line is a serialized `KnowledgeNote`. Read all → render the active set
into Agent 2's prompt as a "lessons learned" section.

Why JSONL: zero-fuss append, replayable, diffable in git, no schema migration
hell. The dataset is small (1 note per analyzed episode × handful of impacts)
so we don't need a real DB.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pipeline.schemas import KnowledgeImpact, KnowledgeNote


DEFAULT_PATH = Path(__file__).resolve().parent.parent.parent / "knowledge" / "notes.jsonl"


class KnowledgeBase:
    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    # ---------- read ---------- #

    def all_notes(self) -> List[KnowledgeNote]:
        notes: List[KnowledgeNote] = []
        with self.path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    notes.append(KnowledgeNote.model_validate_json(line))
                except Exception:
                    # Skip corrupt lines rather than crash the writer.
                    continue
        return notes

    def by_id(self) -> Dict[str, KnowledgeNote]:
        return {n.id: n for n in self.all_notes()}

    def by_impact(self) -> Dict[KnowledgeImpact, List[KnowledgeNote]]:
        out: Dict[KnowledgeImpact, List[KnowledgeNote]] = defaultdict(list)
        for n in self.all_notes():
            out[n.impacts].append(n)
        return out

    # ---------- write ---------- #

    def append(self, note: KnowledgeNote) -> None:
        # Dedup by id — silently skip if already present.
        if note.id in self.by_id():
            return
        with self.path.open("a") as f:
            f.write(note.model_dump_json() + "\n")

    def append_many(self, notes: Iterable[KnowledgeNote]) -> int:
        existing = set(self.by_id())
        n_added = 0
        with self.path.open("a") as f:
            for note in notes:
                if note.id in existing:
                    continue
                f.write(note.model_dump_json() + "\n")
                existing.add(note.id)
                n_added += 1
        return n_added

    # ---------- rendering for Agent 2's prompt ---------- #

    def render_for_writer(
        self, *, max_per_impact: int = 3, min_confidence: str = "medium"
    ) -> str:
        """Return a markdown block suitable for appending to the writer's
        user message (not the system prompt — we don't want to invalidate
        the cached prefix every time a new note is added)."""
        order = ["high", "medium", "low"]
        threshold_idx = order.index(min_confidence)
        sections: List[str] = []
        for impact, notes in self.by_impact().items():
            filtered = [
                n for n in notes if order.index(n.confidence) <= threshold_idx
            ]
            filtered.sort(
                key=lambda n: (order.index(n.confidence), n.created_at), reverse=False
            )
            if not filtered:
                continue
            sections.append(f"### {impact.value}")
            for n in filtered[:max_per_impact]:
                sections.append(f"- ({n.confidence}) {n.finding}")

        if not sections:
            return ""
        return "## Lessons learned (from Agent 6)\n\n" + "\n".join(sections)
