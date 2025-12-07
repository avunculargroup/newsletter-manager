"""End-to-end workflow that powers newsletter generation."""
from __future__ import annotations

import textwrap
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from ..logger import get_logger
from ..services.content_sources import content_source_service
from ..services.image_service import image_service
from ..services.llm_service import NewsletterSection, llm_service
from ..services.mailjet_service import mailjet_service
from ..services.supabase_service import supabase_service
from ..services.template_renderer import renderer

logger = get_logger(__name__)


def html_to_text(html: str) -> str:
    """Extremely small HTML-to-text helper until a richer lib is added."""

    return textwrap.dedent(
        html.replace("<br>", "\n")
        .replace("<br />", "\n")
        .replace("</p>", "\n\n")
        .replace("<li>", "- ")
        .replace("</li>", "\n")
        .replace("<strong>", "")
        .replace("</strong>", "")
        .replace("<em>", "")
        .replace("</em>", "")
    )


class NewsletterPipeline:
    def run(self, topics: List[str], metadata: Dict[str, str]) -> Dict[str, object]:
        run_id = metadata.get("run_id", str(uuid4()))
        supabase_service.record_run({"id": run_id, "status": "running", "topics": topics})
        logger.info("pipeline.start", run_id=run_id, topics=topics)

        try:
            rss_feeds = metadata.get("rss_feeds", []) if isinstance(metadata.get("rss_feeds"), list) else None
            articles = content_source_service.collect(topics, rss_feeds=rss_feeds)
            sections: List[NewsletterSection] = llm_service.generate_sections(articles)
            hero = image_service.fetch(metadata.get("hero_query", topics[0] if topics else "news"))
            mjml_markup, html = renderer.render(
                sections,
                hero,
                metadata={
                    "generated_at": datetime.now(timezone.utc).strftime("%B %d, %Y"),
                    "title": metadata.get("title", "Weekly Brief"),
                },
            )
            supabase_service.save_draft_sections(
                run_id,
                [section.__dict__ for section in sections],
                html,
                hero.__dict__ if hero else None,
            )
            text_version = html_to_text(html)
            mailjet_service.create_draft(metadata.get("subject", "Weekly Brief"), metadata.get("preheader", ""), html, text_version)
            supabase_service.update_run_status(run_id, "completed", "Draft created")
            logger.info("pipeline.completed", run_id=run_id)
            return {
                "run_id": run_id,
                "sections": [section.__dict__ for section in sections],
                "hero": hero.__dict__ if hero else None,
                "html": html,
                "mjml": mjml_markup,
            }
        except Exception as exc:  # pragma: no cover - best-effort logging
            logger.exception("pipeline.failed", run_id=run_id)
            supabase_service.update_run_status(run_id, "failed", str(exc))
            raise


pipeline = NewsletterPipeline()
