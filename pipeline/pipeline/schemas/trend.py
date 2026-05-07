"""Schemas for Agent 1 (Idea Scout)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

from .concept import Concept


class TrendItem(BaseModel):
    """A single signal pulled from an external feed.

    Sources are heterogeneous (Reddit posts, YouTube trending, manual seeds),
    but they all collapse into the same shape here: a piece of mundane source
    material the Rock could form an opinion about.
    """

    source: str = Field(..., description="e.g. 'reddit:r/mildlyinfuriating', 'manual'.")
    title: str = Field(..., max_length=300)
    summary: Optional[str] = Field(default=None, max_length=1000)
    url: Optional[str] = None
    score: Optional[int] = Field(
        default=None,
        description="Source-native popularity (upvotes / view count). Optional.",
    )
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdeaBatch(BaseModel):
    """The artifact emitted by Agent 1, consumed by Agent 2."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sources_used: List[str]
    raw_candidates_count: int = Field(
        ...,
        description="Total TrendItems considered before Claude filtered to top N.",
    )
    candidates: List[Concept] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Top concepts ready to feed into Agent 2 (Writer).",
    )
