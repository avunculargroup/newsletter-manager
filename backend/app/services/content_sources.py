"""Content acquisition layer (NewsAPI, RSS, Firecrawl MCP)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Sequence

import feedparser
import httpx

from ..config import get_settings
from ..logger import get_logger
from ..utils.dedupe import dedupe_by_key

logger = get_logger(__name__)


@dataclass
class ArticleCandidate:
    title: str
    url: str
    source: str
    published_at: datetime
    summary: str | None = None
    image_url: str | None = None
    raw: Dict[str, object] = field(default_factory=dict)


class ContentSourceService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.http = httpx.Client(timeout=httpx.Timeout(15.0, connect=5.0))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def collect(
        self,
        topics: Sequence[str],
        hours: int = 72,
        rss_feeds: Sequence[str] | None = None,
    ) -> List[ArticleCandidate]:
        """Collect and deduplicate articles across the configured sources."""

        window_start = datetime.now(timezone.utc) - timedelta(hours=hours)
        articles: List[ArticleCandidate] = []
        articles.extend(self._from_newsapi(topics, window_start))
        if rss_feeds:
            articles.extend(self._from_rss(rss_feeds))
        articles.extend(self._from_firecrawl_search(topics))

        deduped = dedupe_by_key(articles, attr="url")
        logger.info("content_sources.collected", count=len(deduped), original=len(articles))
        return deduped

    # ------------------------------------------------------------------
    # Source specific helpers
    # ------------------------------------------------------------------
    def _from_newsapi(self, topics: Sequence[str], start: datetime) -> List[ArticleCandidate]:
        if not self.settings.newsapi_key:
            logger.warning("content_sources.newsapi.disabled", reason="missing NEWSAPI_KEY")
            return []

        results: List[ArticleCandidate] = []
        base_url = "https://newsapi.org/v2/everything"
        for topic in topics:
            params = {
                "q": topic,
                "from": start.isoformat(),
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 50,
            }
            response = self.http.get(
                base_url,
                params=params,
                headers={"X-Api-Key": self.settings.newsapi_key},
            )
            response.raise_for_status()
            payload = response.json()
            for article in payload.get("articles", []):
                published = article.get("publishedAt") or start.isoformat()
                candidate = ArticleCandidate(
                    title=article.get("title") or "Untitled",
                    url=article.get("url"),
                    source="newsapi",
                    published_at=datetime.fromisoformat(published.replace("Z", "+00:00")),
                    summary=article.get("description"),
                    image_url=article.get("urlToImage"),
                    raw=article,
                )
                results.append(candidate)
        return results

    def _from_rss(self, feeds: Sequence[str]) -> List[ArticleCandidate]:
        results: List[ArticleCandidate] = []
        for feed in feeds:
            parsed = feedparser.parse(feed)
            for entry in parsed.entries:
                published_parsed = entry.get("published_parsed")
                published = (
                    datetime(*published_parsed[:6], tzinfo=timezone.utc)
                    if published_parsed
                    else datetime.now(timezone.utc)
                )
                candidate = ArticleCandidate(
                    title=entry.get("title", "Untitled"),
                    url=entry.get("link"),
                    source="rss",
                    published_at=published,
                    summary=entry.get("summary"),
                    raw={"feed": feed, "entry": entry.get("id")},
                )
                results.append(candidate)
        return results

    def _from_firecrawl_search(self, topics: Sequence[str]) -> List[ArticleCandidate]:
        if not (self.settings.firecrawl_api_key and self.settings.firecrawl_server_url):
            return []

        results: List[ArticleCandidate] = []
        endpoint = f"{self.settings.firecrawl_server_url}/v1/search"
        for topic in topics:
            payload = {"query": topic, "limit": 5}
            response = self.http.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.settings.firecrawl_api_key}"},
            )
            if response.status_code >= 400:
                logger.error(
                    "content_sources.firecrawl.error",
                    status=response.status_code,
                    body=response.text,
                )
                continue
            data = response.json()
            for item in data.get("results", []):
                published_raw = item.get("published_at") or datetime.now(timezone.utc).isoformat()
                published_at = datetime.fromisoformat(str(published_raw).replace("Z", "+00:00"))
                candidate = ArticleCandidate(
                    title=item.get("title", "Untitled"),
                    url=item.get("url"),
                    source="firecrawl",
                    published_at=published_at,
                    summary=item.get("snippet"),
                    raw=item,
                )
                results.append(candidate)
        return results


content_source_service = ContentSourceService()
