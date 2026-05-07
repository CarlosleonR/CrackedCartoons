"""Manual seed source — load TrendItems from a JSON file or hardcoded list.

Useful for offline testing and for when you have ideas you want to feed in
directly without scraping anything.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Sequence, Union

from pipeline.schemas import TrendItem
from .base import TrendSource


# A small built-in seed list so the pipeline always has *something* to chew on.
BUILTIN_SEEDS: Sequence[dict] = (
    {"title": "Drive-thru order accuracy", "summary": "The Rock has thoughts about getting the wrong fries."},
    {"title": "Self-checkout machine etiquette", "summary": "Item not in bagging area. The Rock weighs in."},
    {"title": "How people fold towels", "summary": "Rolled vs. folded. The Rock has a system."},
    {"title": "Coffee shop laptop campers", "summary": "Three hours, one drink. The Rock is appalled."},
    {"title": "Loud chewing on public transit", "summary": "Apple in a quiet train car. The Rock issues a verdict."},
    {"title": "Kids' birthday party gift bags", "summary": "Industrial complex. The Rock disapproves of party favors."},
    {"title": "How tall a sandwich should be", "summary": "Anything over four inches is a stunt."},
    {"title": "Whether cereal is a soup", "summary": "He has researched this for years."},
)


class ManualSource(TrendSource):
    name = "manual"

    def __init__(
        self,
        items: Optional[Sequence[Union[dict, TrendItem]]] = None,
        path: Optional[Path] = None,
    ) -> None:
        loaded: List[TrendItem] = []
        if path is not None:
            data = json.loads(Path(path).read_text())
            for d in data:
                loaded.append(TrendItem.model_validate({**d, "source": d.get("source", "manual")}))
        elif items is not None:
            for d in items:
                if isinstance(d, TrendItem):
                    loaded.append(d)
                else:
                    loaded.append(TrendItem.model_validate({**d, "source": d.get("source", "manual")}))
        else:
            for d in BUILTIN_SEEDS:
                loaded.append(TrendItem.model_validate({**d, "source": "manual:builtin"}))
        self._items = loaded

    def fetch(self, limit: int = 25) -> List[TrendItem]:
        return list(self._items[:limit])
