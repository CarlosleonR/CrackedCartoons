"""Schemas for Agent 4 (Quality Check)."""
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Severity = Literal["error", "warning", "info"]


class QualityIssue(BaseModel):
    severity: Severity
    code: str = Field(..., description="Stable, machine-readable identifier.")
    message: str
    affected_frame: Optional[int] = None
    affected_scene_id: Optional[str] = None
    affected_file: Optional[str] = None


class QualityReport(BaseModel):
    episode_id: str
    video_path: str
    passed: bool

    duration_seconds_actual: float = 0.0
    duration_seconds_expected: float = 0.0
    duration_drift_seconds: float = 0.0

    audio_files_total: int = 0
    audio_files_missing: int = 0

    sampled_frames: int = 0
    blank_frames: int = 0

    issues: List[QualityIssue] = Field(default_factory=list)

    @property
    def errors(self) -> List[QualityIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[QualityIssue]:
        return [i for i in self.issues if i.severity == "warning"]
