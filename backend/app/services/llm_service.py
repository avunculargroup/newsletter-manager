"""LLM orchestration via OpenRouter."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Sequence

import httpx

from ..config import get_settings
from ..logger import get_logger
from .content_sources import ArticleCandidate

logger = get_logger(__name__)


@dataclass
class NewsletterSection:
    title: str
    hook: str
    summary: str
    call_to_action: str
    keywords: List[str]
    source_url: str


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.http = httpx.Client(
            base_url=str(self.settings.openrouter_base_url),
            headers={
                "Authorization": f"Bearer {self.settings.openrouter_api_key}" if self.settings.openrouter_api_key else "",
                "HTTP-Referer": "newsletter-manager",
                "X-Title": "Automated Newsletter Platform",
            },
            timeout=60.0,
        )

    def generate_sections(
        self,
        articles: Sequence[ArticleCandidate],
        max_sections: int = 5,
        tone: str = "conversational",
    ) -> List[NewsletterSection]:
        if not self.settings.openrouter_api_key:
            logger.warning("llm.fallback", reason="missing OPENROUTER_API_KEY")
            return self._fallback_sections(articles, max_sections)

        content_payload = [
            {
                "title": article.title,
                "url": article.url,
                "summary": article.summary,
                "published_at": article.published_at.isoformat(),
            }
            for article in articles[:20]
        ]

        system_prompt = (
            "You are an editorial assistant who creates a concise tech newsletter. "
            "Return JSON that strictly matches the `sections` schema."
        )
        user_prompt = {
            "tone": tone,
            "max_sections": max_sections,
            "articles": content_payload,
            "output_schema": {
                "type": "object",
                "properties": {
                    "sections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "hook": {"type": "string"},
                                "summary": {"type": "string"},
                                "call_to_action": {"type": "string"},
                                "keywords": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "source_url": {"type": "string", "format": "uri"},
                            },
                            "required": [
                                "title",
                                "summary",
                                "call_to_action",
                                "keywords",
                                "source_url",
                                "hook",
                            ],
                        },
                    }
                },
                "required": ["sections"],
            },
        }

        response = self.http.post(
            "/chat/completions",
            json={
                "model": self.settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_prompt)},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_schema", "json_schema": user_prompt["output_schema"]},
            },
        )
        if response.status_code >= 400:
            logger.error("llm.error", status=response.status_code, body=response.text)
            return self._fallback_sections(articles, max_sections)

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        sections_payload = parsed.get("sections", [])
        return [
            NewsletterSection(
                title=item["title"],
                hook=item["hook"],
                summary=item["summary"],
                call_to_action=item["call_to_action"],
                keywords=item.get("keywords", []),
                source_url=item["source_url"],
            )
            for item in sections_payload
        ]

    def _fallback_sections(
        self, articles: Sequence[ArticleCandidate], max_sections: int
    ) -> List[NewsletterSection]:
        sections: List[NewsletterSection] = []
        for article in articles[:max_sections]:
            hook = article.summary or f"Why {article.title} matters"
            section = NewsletterSection(
                title=article.title,
                hook=hook,
                summary=(article.summary or "Summary unavailable."),
                call_to_action=f"Read the full story on {article.source}.",
                keywords=[article.source],
                source_url=article.url,
            )
            sections.append(section)
        return sections


llm_service = LLMService()
