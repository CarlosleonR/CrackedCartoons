"""Read-side YouTube wrapper used by Agent 6 (Analyst).

Pulls two kinds of data:
- Public stats from `youtube.videos.list` (statistics part) — always works.
- Owner-only metrics from `youtubeAnalytics.reports.query` — requires the
  YouTube Analytics API enabled in the GCP project AND the channel to own
  the video. We attempt this and gracefully degrade if it 403s.
- Comments from `youtube.commentThreads.list`.

Reuses the same OAuth flow as `youtube_uploader.py`. Adds the read-only
analytics scope so the same token works for both upload and read.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pipeline.agents.youtube_uploader import (
    DEFAULT_CLIENT_SECRET,
    DEFAULT_TOKEN_PATH,
)
from pipeline.schemas import CommentSample, VideoMetrics


# Adds analytics scope to the upload scopes so a single OAuth flow covers both.
ANALYST_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


class YouTubeAnalyticsError(RuntimeError):
    pass


class YouTubeAnalyticsClient:
    def __init__(
        self,
        client_secret_path: Path = DEFAULT_CLIENT_SECRET,
        token_path: Path = DEFAULT_TOKEN_PATH,
    ) -> None:
        self.client_secret_path = client_secret_path
        self.token_path = token_path
        self.scopes = ANALYST_SCOPES
        if not self.client_secret_path.exists():
            raise YouTubeAnalyticsError(
                f"OAuth client secret missing: {self.client_secret_path}"
            )
        self._creds: Optional[Credentials] = None
        self._youtube = None
        self._analytics = None

    # ---------- public API ---------- #

    def fetch_metrics(
        self, *, video_id: str, published_at: Optional[datetime] = None
    ) -> VideoMetrics:
        creds = self._authorize()
        youtube = self._youtube_client(creds)

        # Public stats — always available.
        resp = (
            youtube.videos()
            .list(part="statistics,snippet", id=video_id)
            .execute()
        )
        items = resp.get("items", [])
        if not items:
            raise YouTubeAnalyticsError(f"Video {video_id} not found.")
        item = items[0]
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})

        published = (
            published_at
            or _parse_iso8601(snippet.get("publishedAt", ""))
            or datetime.now(timezone.utc)
        )
        age_hours = (datetime.now(timezone.utc) - published).total_seconds() / 3600.0

        m = VideoMetrics(
            video_id=video_id,
            age_hours=age_hours,
            views=int(stats.get("viewCount", 0)),
            likes=int(stats.get("likeCount", 0)),
            comments_count=int(stats.get("commentCount", 0)),
        )

        # Owner-only metrics — best-effort.
        try:
            self._enrich_with_analytics(m, video_id=video_id, since=published)
        except HttpError as e:
            print(
                f"[analytics] Analytics API call failed (will continue with "
                f"public stats only): {e}",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"[analytics] Analytics API skipped: {e}", file=sys.stderr)

        return m

    def fetch_top_comments(
        self, *, video_id: str, limit: int = 25
    ) -> List[CommentSample]:
        creds = self._authorize()
        youtube = self._youtube_client(creds)
        try:
            resp = (
                youtube.commentThreads()
                .list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=min(limit, 100),
                    order="relevance",
                    textFormat="plainText",
                )
                .execute()
            )
        except HttpError as e:
            # 403 commentsDisabled is common; degrade silently.
            print(f"[analytics] comments fetch failed: {e}", file=sys.stderr)
            return []

        out: List[CommentSample] = []
        for thread in resp.get("items", []):
            top = thread.get("snippet", {}).get("topLevelComment", {})
            top_snip = top.get("snippet", {})
            out.append(
                CommentSample(
                    author=top_snip.get("authorDisplayName", "?"),
                    text=top_snip.get("textDisplay", "")[:1500],
                    likes=int(top_snip.get("likeCount", 0)),
                    published_at=_parse_iso8601(top_snip.get("publishedAt", ""))
                                  or datetime.now(timezone.utc),
                    is_reply=False,
                )
            )
        return out[:limit]

    # ---------- internals ---------- #

    def _enrich_with_analytics(
        self, m: VideoMetrics, *, video_id: str, since: datetime
    ) -> None:
        creds = self._authorize()
        analytics = self._analytics_client(creds)
        end_date = datetime.now(timezone.utc).date().isoformat()
        start_date = (since.date() - timedelta(days=1)).isoformat()
        metrics = (
            "views,estimatedMinutesWatched,averageViewDuration,"
            "averageViewPercentage,subscribersGained,subscribersLost,shares,"
            "annotationImpressions,annotationClickThroughRate"
        )
        # Note: impressions / impressionsCtr are Studio-only and require
        # different metric names — `card` and `cardImpressions` aren't the
        # same. We expose them as None for now; see ANALYST.md for upgrades.
        resp = (
            analytics.reports()
            .query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics=metrics,
                dimensions="video",
                filters=f"video=={video_id}",
            )
            .execute()
        )
        rows = resp.get("rows") or []
        if not rows:
            return
        headers = [h["name"] for h in resp.get("columnHeaders", [])]
        row = dict(zip(headers, rows[0]))

        m.avg_view_duration_seconds = _safe_float(row.get("averageViewDuration"))
        m.avg_view_percentage = _safe_float(row.get("averageViewPercentage"))
        m.subscribers_gained = _safe_int(row.get("subscribersGained"))
        m.subscribers_lost = _safe_int(row.get("subscribersLost"))
        m.shares = _safe_int(row.get("shares"))

    def _authorize(self) -> Credentials:
        if self._creds and self._creds.valid:
            return self._creds

        creds: Optional[Credentials] = None
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(self.token_path.read_text()), self.scopes
                )
            except Exception:
                creds = None

        if creds and creds.valid and self._has_scopes(creds):
            self._creds = creds
            return creds
        if (
            creds
            and creds.expired
            and creds.refresh_token
            and self._has_scopes(creds)
        ):
            creds.refresh(Request())
            self._save_token(creds)
            self._creds = creds
            return creds

        # Either no token, or it's missing the analytics scope. Re-auth.
        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.client_secret_path), self.scopes
        )
        creds = flow.run_local_server(port=0, prompt="consent")
        self._save_token(creds)
        self._creds = creds
        return creds

    def _has_scopes(self, creds: Credentials) -> bool:
        granted = set(getattr(creds, "scopes", None) or [])
        return all(s in granted for s in self.scopes)

    def _save_token(self, creds: Credentials) -> None:
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        self.token_path.write_text(creds.to_json())

    def _youtube_client(self, creds: Credentials):
        if self._youtube is None:
            self._youtube = build(
                "youtube", "v3", credentials=creds, cache_discovery=False
            )
        return self._youtube

    def _analytics_client(self, creds: Credentials):
        if self._analytics is None:
            self._analytics = build(
                "youtubeAnalytics", "v2", credentials=creds, cache_discovery=False
            )
        return self._analytics


# ---------- small helpers ---------- #

def _parse_iso8601(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _safe_float(v) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _safe_int(v) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None
