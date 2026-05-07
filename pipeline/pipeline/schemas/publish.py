"""Publish-side schemas: YouTube metadata + thumbnail spec.

Both are produced by the PublisherAgent (Claude) and consumed by the YouTube
uploader and the generic Remotion thumbnail composition respectively.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------- YouTube metadata ---------- #

class YouTubeCategory(str, Enum):
    """Subset of YouTube video category IDs that fit the show."""
    comedy = "23"
    entertainment = "24"
    film_and_animation = "1"


class PrivacyStatus(str, Enum):
    private = "private"
    unlisted = "unlisted"
    public = "public"


class PublishMetadata(BaseModel):
    """Everything the YouTube videos.insert call needs."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="YouTube title. Avoid <, >, |. Aim for 50-80 chars.",
    )
    description: str = Field(
        ...,
        max_length=5000,
        description="Description. Include CTA + #Shorts hashtag.",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Up to ~15 tags. Total length must stay under 500 chars.",
    )
    category_id: YouTubeCategory = YouTubeCategory.comedy

    # Defaults; CLI flags override.
    privacy_status: PrivacyStatus = PrivacyStatus.private
    made_for_kids: bool = False
    notify_subscribers: bool = True
    publish_at: Optional[datetime] = Field(
        default=None,
        description=(
            "If set, YouTube auto-publishes at this UTC time. Requires "
            "privacy_status=private at upload; status flips to public at the "
            "scheduled moment."
        ),
    )


# ---------- Thumbnail spec ---------- #

class ThumbnailMood(str, Enum):
    angry = "angry"
    smug = "smug"
    shocked = "shocked"
    indignant = "indignant"
    deadpan = "deadpan"


class ThumbnailLayout(str, Enum):
    """How the visual elements arrange. Each maps to a layout branch in
    src/episodes/ThumbnailFromScript.tsx."""
    rock_left_object_right = "rock_left_object_right"
    rock_center_score_overlay = "rock_center_score_overlay"
    rock_only_big_text = "rock_only_big_text"


class ThumbnailSpec(BaseModel):
    """Compact, layout-driven spec for the generic thumbnail composition."""

    background_color: str = Field(
        default="#f5b73a",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Dominant background hex.",
    )
    accent_color: str = Field(
        default="#d94a3a",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Drop-shadow / sticker accent color.",
    )
    episode_badge: str = Field(
        ...,
        max_length=8,
        description="Top-left badge text. e.g. 'EP. 1', 'EP. 12'.",
    )
    headline: str = Field(
        ...,
        max_length=24,
        description="Big bold headline. Use \\n to wrap. e.g. 'NOBODY\\nASKED.'",
    )
    callout: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Sticker callout near the rock. e.g. '← rates your sandwich'.",
    )
    score: Optional[str] = Field(
        default=None,
        max_length=6,
        description="Score stamp text. e.g. '0/10', '-3/10', 'F'.",
    )
    footer: str = Field(
        default="the rock has thoughts",
        max_length=40,
        description="Tiny footer label.",
    )
    mood: ThumbnailMood = ThumbnailMood.angry
    layout: ThumbnailLayout = ThumbnailLayout.rock_left_object_right


# ---------- combined output ---------- #

class PublishPackage(BaseModel):
    """One artifact emitted by Agent 5 covering both metadata and thumbnail."""

    metadata: PublishMetadata
    thumbnail: ThumbnailSpec
