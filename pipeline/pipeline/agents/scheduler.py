"""Pick a smart upload time.

YouTube Shorts performance is consistency-driven, but two heuristics still help:
- **Day**: Thu/Fri/Sat/Sun catch the weekend lean-in.
- **Hour**: Mid-afternoon (14:00 local) catches lunch-break browsing AND seeds
  evening recommendations.

Once Agent 6 has accumulated enough analytics, this module should be replaced
with a per-channel optimum derived from "when does my audience watch?". For
now, the heuristic is the floor.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Optional


# Mon=0 ... Sun=6
PREFERRED_DAYS = (3, 4, 5, 6)  # Thu, Fri, Sat, Sun
PREFERRED_HOUR_LOCAL = 14
PREFERRED_MINUTE = 0
MIN_LEAD_TIME = timedelta(hours=1)


@dataclass
class ScheduleSlot:
    publish_at_utc: datetime
    rationale: str

    def to_iso8601_z(self) -> str:
        # YouTube wants ISO 8601 with 'Z' suffix.
        return self.publish_at_utc.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _local_now(tz: Optional[timezone]) -> datetime:
    if tz is None:
        # Use system local.
        return datetime.now().astimezone()
    return datetime.now(tz=tz)


def pick_publish_at(
    *,
    now: Optional[datetime] = None,
    tz: Optional[timezone] = None,
    preferred_days=PREFERRED_DAYS,
    preferred_hour: int = PREFERRED_HOUR_LOCAL,
    min_lead: timedelta = MIN_LEAD_TIME,
) -> ScheduleSlot:
    """Return the next preferred local-time slot at least `min_lead` ahead.

    Search forward day-by-day up to 14 days; if nothing matches (would only
    happen with an empty preferred_days), fall back to `now + min_lead`.
    """
    if now is None:
        now = _local_now(tz)
    elif now.tzinfo is None:
        # Naive — assume local.
        now = now.astimezone() if hasattr(now, "astimezone") else now
    earliest = now + min_lead

    for offset in range(0, 14):
        candidate_date = (earliest + timedelta(days=offset)).date()
        if candidate_date.weekday() not in preferred_days:
            continue
        candidate_local = datetime.combine(
            candidate_date,
            time(hour=preferred_hour, minute=PREFERRED_MINUTE),
            tzinfo=now.tzinfo,
        )
        if candidate_local < earliest:
            # Too soon today; try the next preferred day.
            continue
        return ScheduleSlot(
            publish_at_utc=candidate_local.astimezone(timezone.utc),
            rationale=(
                f"{candidate_local:%A %Y-%m-%d %H:%M %Z} — preferred day "
                f"{candidate_local.strftime('%A')} at "
                f"{candidate_local.strftime('%H:%M')} local."
            ),
        )

    # Fallback: just `now + min_lead`.
    return ScheduleSlot(
        publish_at_utc=earliest.astimezone(timezone.utc),
        rationale=(
            "No preferred slot found within 14 days; defaulting to "
            f"{earliest:%Y-%m-%d %H:%M %Z}."
        ),
    )


def parse_iso8601_to_utc(s: str) -> datetime:
    """Parse a user-provided ISO 8601 string to a UTC datetime."""
    s = s.strip()
    if s.endswith("Z"):
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # Assume local.
        dt = dt.astimezone()
    return dt.astimezone(timezone.utc)
