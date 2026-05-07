"""Schemas for Agent 6 (Analyst).

Two layers:
- Raw observation (`VideoMetrics`, `CommentSample`) — what we fetch.
- Analyst output (`EpisodeReport`, `KnowledgeNote`) — what Claude produces.

The KnowledgeNote layer is the closed-loop output: notes are persisted and
injected into Agent 2's prompt on subsequent runs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ---------- raw observations ---------- #

class VideoMetrics(BaseModel):
    """A single snapshot of a video's stats. Take multiple at 24/48/72h to
    spot retention curves. Most fields are optional because the Analytics API
    isn't always available (separate scope, channel must own the video,
    metrics are sometimes not yet computed for very fresh videos)."""

    video_id: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    age_hours: Optional[float] = None
    views: int = 0
    likes: int = 0
    comments_count: int = 0
    impressions: Optional[int] = None
    impressions_ctr: Optional[float] = Field(
        default=None, ge=0, le=1,
        description="Click-through rate from impressions. 0..1.",
    )
    avg_view_duration_seconds: Optional[float] = None
    avg_view_percentage: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Percent of video watched on average. 0..100.",
    )
    subscribers_gained: Optional[int] = None
    subscribers_lost: Optional[int] = None
    shares: Optional[int] = None


class CommentSample(BaseModel):
    author: str
    text: str
    likes: int = 0
    published_at: datetime
    is_reply: bool = False


# ---------- analyst output ---------- #

class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    mixed = "mixed"


class EpisodeReport(BaseModel):
    """One self-contained read on how an episode is doing.

    Produced by the AnalystAgent; not persisted into the long-term knowledge
    base — instead, derived `KnowledgeNote`s are.
    """

    episode_id: str
    video_id: str
    title: str
    metrics: VideoMetrics
    top_comments: List[CommentSample] = Field(default_factory=list)
    sentiment: Sentiment = Sentiment.neutral
    what_worked: List[str] = Field(
        default_factory=list,
        description="Concrete, specific. e.g. 'Title front-loaded the bit'.",
    )
    what_didnt: List[str] = Field(
        default_factory=list,
        description="Concrete, specific. e.g. 'Pacing dragged through scene 4'.",
    )
    suggestions_for_writer: List[str] = Field(
        default_factory=list,
        description="Actionable rewrites. e.g. 'Open with the conflict, not the setup'.",
    )
    raw_summary: str = Field(
        default="",
        max_length=2000,
        description="Free-form analyst summary used as evidence for the bullets.",
    )


class KnowledgeImpact(str, Enum):
    """Which part of Agent 2's output a learning impacts."""
    hook = "hook"
    pacing = "pacing"
    punchline = "punchline"
    voice = "voice"
    thumbnail = "thumbnail"
    title = "title"
    structure = "structure"


class KnowledgeNote(BaseModel):
    """A single learning that Agent 2 should consider on the NEXT script.

    These are the closed-loop output. Persisted append-only to a JSONL file
    and injected into the writer's prompt as a 'lessons learned' section.
    """

    id: str = Field(
        ...,
        pattern=r"^kn-[a-z0-9-]+$",
        description="Stable id, e.g. 'kn-2026-05-airport-hook-late'.",
    )
    derived_from: List[str] = Field(
        ...,
        min_length=1,
        description="episode_ids or video_ids this note draws on.",
    )
    finding: str = Field(
        ...,
        min_length=10,
        max_length=240,
        description="One sentence. Concrete. Action-shaped. Not 'be funny'.",
    )
    impacts: KnowledgeImpact
    confidence: Literal["low", "medium", "high"] = "medium"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: Optional[str] = Field(
        default=None,
        max_length=600,
        description="Optional supporting comment / metric snippet.",
    )


class AnalystOutput(BaseModel):
    """What the Analyst tool returns — the report PLUS any new knowledge notes."""

    report: EpisodeReport
    new_knowledge: List[KnowledgeNote] = Field(default_factory=list)
