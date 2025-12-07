"""Pydantic schemas shared across routers."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class TopicPreset(BaseModel):
    id: Optional[str] = None
    name: str
    topics: List[str]
    rss_feeds: List[HttpUrl] | None = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RunRequest(BaseModel):
    topics: List[str]
    title: str = "Weekly Brief"
    subject: str = "Weekly Brief"
    preheader: str = ""
    hero_query: str | None = None
    rss_feeds: List[HttpUrl] | None = None


class RunResponse(BaseModel):
    run_id: str
    status: str
    message: str | None = None


class DraftSection(BaseModel):
    title: str
    hook: str
    summary: str
    call_to_action: str
    keywords: List[str]
    source_url: HttpUrl


class DraftResponse(BaseModel):
    run_id: str
    hero: dict | None
    sections: List[DraftSection]
    html: str


class RunStatus(BaseModel):
    id: str
    status: str
    created_at: datetime | None = None
    message: str | None = None
    topics: List[str] | None = None
