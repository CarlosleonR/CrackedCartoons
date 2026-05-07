"""Output schema produced by Agent 2 (Writer) and consumed by Agent 3 (Production).

Strict enough that Agent 3 can map straight to Remotion scene components, loose
enough (`props: dict`) to admit new scene types without schema migrations.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# ---------- enums ---------- #

class Speaker(str, Enum):
    rock = "rock"
    kid = "kid"
    narrator = "narrator"
    other = "other"


class Emotion(str, Enum):
    smug = "smug"
    angry = "angry"
    indignant = "indignant"
    confused = "confused"
    deadpan = "deadpan"
    shocked = "shocked"
    excited = "excited"
    sad = "sad"
    hostile = "hostile"


class SceneType(str, Enum):
    """Each value maps to a Remotion component Agent 3 can render.

    Adding new types is fine — Agent 3 falls back to a generic renderer
    using the scene's `props` and `description`.
    """
    title_card = "title_card"
    character_entrance = "character_entrance"
    rating_beat = "rating_beat"
    dialogue_exchange = "dialogue_exchange"
    reaction_beat = "reaction_beat"
    montage = "montage"
    outro = "outro"


# ---------- nested ---------- #

class DialogueLine(BaseModel):
    """A single voiceover line. Maps 1:1 to an ElevenLabs TTS call and one
    `<Audio>` mounted at `start_frame` in the Remotion composition."""

    speaker: Speaker
    text: str = Field(..., description="The exact spoken text fed to ElevenLabs.")
    on_screen_text: Optional[str] = Field(
        default=None,
        description=(
            "Speech-bubble text. Often the same as `text` but may be shorter / "
            "ALL-CAPS / line-broken with \\n for visual punch."
        ),
    )
    emotion: Optional[Emotion] = None
    start_frame: int = Field(..., ge=0, description="Absolute frame in the episode.")
    estimated_duration_frames: int = Field(
        ...,
        gt=0,
        description="Writer's estimate; production agent re-measures the rendered MP3.",
    )
    scene_id: str = Field(..., description="ID of the scene this line plays inside.")


class SFXCue(BaseModel):
    """Sound effect cue. The `description` is fed verbatim to ElevenLabs Sound
    Effects API or matched against a local SFX library."""

    description: str = Field(
        ...,
        description="Natural-language SFX prompt, e.g. 'cartoon record scratch, sudden stop'.",
    )
    start_frame: int = Field(..., ge=0)
    duration_seconds: float = Field(..., gt=0.0, le=22.0)
    volume: float = Field(default=0.6, ge=0.0, le=1.0)
    scene_id: str
    reuse_key: Optional[str] = Field(
        default=None,
        description=(
            "If multiple cues share this key, Agent 3 generates the SFX once "
            "and reuses the file. e.g. 'stamp_ding' across three rating beats."
        ),
    )


class Scene(BaseModel):
    id: str = Field(..., description="Stable, kebab-case. e.g. 'title-card', 'rating-1'.")
    type: SceneType
    start_frame: int = Field(..., ge=0)
    duration_frames: int = Field(..., gt=0)
    description: str = Field(
        ...,
        description="One paragraph the production agent uses to wire visuals.",
    )
    props: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Scene-specific props. Reference shapes per `type`:\n"
            "- title_card: {episode_number, headline, subtitle}\n"
            "- character_entrance: {character, entrance_direction, on_screen_label, "
            "background_props: list[str]}\n"
            "- rating_beat: {subject, subject_variant, score, hero_shot_text}\n"
            "- dialogue_exchange: {participants: list[Speaker], setting}\n"
            "- reaction_beat: {character, expression, dots: int}\n"
            "- outro: {big_text, subtitle, tag}"
        ),
    )
    visual_notes: Optional[str] = Field(
        default=None,
        description="Free-form camera / blocking notes for Agent 3.",
    )


# ---------- top level ---------- #

class EpisodeScript(BaseModel):
    """The structured artifact passed from Writer → Production."""

    episode_id: str = Field(
        ..., pattern=r"^Ep\d{2,3}-[A-Za-z0-9-]+$",
        description="e.g. 'Ep02-AirportLines'. Used as Remotion composition id.",
    )
    title: str = Field(..., max_length=70, description="YouTube-friendly title.")
    logline: str = Field(..., max_length=180)
    fps: int = Field(default=30, ge=24, le=60)
    width: int = Field(default=1080)
    height: int = Field(default=1920)
    total_frames: int = Field(..., gt=0)
    structure: str = Field(
        default="setup-escalation-twist-nobody-wins",
        description="Narrative shape. Agent 6's analyst can A/B alternative shapes.",
    )
    scenes: List[Scene] = Field(..., min_length=3)
    voiceover: List[DialogueLine] = Field(default_factory=list)
    sfx: List[SFXCue] = Field(default_factory=list)
    thumbnail_concept: str = Field(
        ...,
        description="One paragraph describing the thumbnail composition for Agent 5.",
    )

    @model_validator(mode="after")
    def _validate_timing(self) -> "EpisodeScript":
        # Scenes must be contiguous and sum to total_frames.
        cursor = 0
        for s in self.scenes:
            if s.start_frame != cursor:
                raise ValueError(
                    f"Scene {s.id!r} starts at {s.start_frame}, expected {cursor}."
                )
            cursor += s.duration_frames
        if cursor != self.total_frames:
            raise ValueError(
                f"Scenes total {cursor} frames but total_frames={self.total_frames}."
            )

        # Audio cues must reference real scenes and start within the episode.
        scene_ids = {s.id for s in self.scenes}
        for line in self.voiceover:
            if line.scene_id not in scene_ids:
                raise ValueError(f"VO line scene_id {line.scene_id!r} not found.")
            if line.start_frame >= self.total_frames:
                raise ValueError(
                    f"VO line at frame {line.start_frame} starts past episode end."
                )
        for cue in self.sfx:
            if cue.scene_id not in scene_ids:
                raise ValueError(f"SFX scene_id {cue.scene_id!r} not found.")
            if cue.start_frame >= self.total_frames:
                raise ValueError(
                    f"SFX at frame {cue.start_frame} starts past episode end."
                )
        return self
