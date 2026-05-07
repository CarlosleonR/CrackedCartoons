"""Reddit source — public JSON endpoint, no API key needed.

Subreddits are picked for *banal opinion fodder*, not news. The whole point of
The Rock is having strong opinions about things he has no business having
opinions about, so we pull from places where banal opinions live: petty
annoyances, hot takes about everyday objects, life advice that shouldn't need
saying.

Avoid politics/news subs intentionally — they age badly and don't fit the show.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import List, Sequence

from pipeline.schemas import TrendItem
from .base import TrendSource


DEFAULT_SUBREDDITS = (
    "mildlyinfuriating",
    "unpopularopinion",
    "AskReddit",
    "ShittyLifeProTips",
    "CasualConversation",
    "tipofmytongue",
    "FoodPorn",
    "BuyItForLife",
)


class RedditSource(TrendSource):
    name = "reddit"

    def __init__(
        self,
        subreddits: Sequence[str] = DEFAULT_SUBREDDITS,
        time_range: str = "week",
        per_sub: int = 5,
        user_agent: str = "cracked-cartoons-idea-scout/0.1 by anonymous",
    ) -> None:
        self.subreddits = list(subreddits)
        self.time_range = time_range
        self.per_sub = per_sub
        self.user_agent = user_agent

    def fetch(self, limit: int = 25) -> List[TrendItem]:
        items: List[TrendItem] = []
        for sub in self.subreddits:
            try:
                items.extend(self._fetch_subreddit(sub))
            except Exception as e:
                print(f"[reddit] {sub} skipped: {e}", file=sys.stderr)
        # Cap globally.
        return items[:limit]

    def _fetch_subreddit(self, sub: str) -> List[TrendItem]:
        url = (
            f"https://www.reddit.com/r/{sub}/top.json"
            f"?t={self.time_range}&limit={self.per_sub}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Rate-limited — bail without crashing the whole batch.
                return []
            raise
        out: List[TrendItem] = []
        for child in payload.get("data", {}).get("children", []):
            d = child.get("data", {})
            if d.get("over_18") or d.get("stickied"):
                continue
            out.append(
                TrendItem(
                    source=f"reddit:r/{sub}",
                    title=(d.get("title") or "")[:300],
                    summary=(d.get("selftext") or "")[:1000] or None,
                    url=f"https://reddit.com{d.get('permalink', '')}",
                    score=d.get("score"),
                )
            )
        return out
