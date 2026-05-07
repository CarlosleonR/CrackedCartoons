"""Input schema: a comedic episode concept produced by Agent 1 (Idea Scout)."""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class Concept(BaseModel):
    """The unit of work consumed by the Writer agent."""

    topic: str = Field(
        ...,
        description="The thing The Rock has no business having opinions about.",
    )
    premise: str = Field(
        ...,
        description="One-sentence setup. Where The Rock encounters the topic.",
    )
    conflict: str = Field(
        ...,
        description="Who pushes back on The Rock and how it escalates.",
    )
    punchline: str = Field(
        ...,
        description="The absurd twist or cosmic deflation that ends the bit.",
    )
    tone_notes: Optional[str] = Field(
        default=None,
        description="Optional flavoring (e.g. 'extra petty', 'almost wistful').",
    )
    runtime_seconds: int = Field(
        default=30,
        ge=15,
        le=60,
        description="Target runtime; YouTube Shorts max 60.",
    )
    inspiration_sources: List[str] = Field(
        default_factory=list,
        description="URLs / references from Idea Scout that inspired the concept.",
    )
