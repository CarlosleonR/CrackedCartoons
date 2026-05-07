"""TrendSource interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from pipeline.schemas import TrendItem


class TrendSource(ABC):
    """Implementations fetch a list of mundane signals the Rock could opine on."""

    name: str

    @abstractmethod
    def fetch(self, limit: int = 25) -> List[TrendItem]:
        """Return up to `limit` TrendItems. Should not raise on transient errors —
        log and return an empty list instead, so one bad source doesn't kill the
        pipeline.
        """
        ...
