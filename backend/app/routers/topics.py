from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.models import TopicPreset
from ..services.supabase_service import supabase_service

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/")
def list_topics() -> list[TopicPreset]:
    return [TopicPreset.model_validate(item) for item in supabase_service.list_topic_presets()]


@router.post("/", response_model=TopicPreset)
def upsert_topic(preset: TopicPreset) -> TopicPreset:
    if not preset.topics:
        raise HTTPException(status_code=400, detail="topics list cannot be empty")
    saved = supabase_service.upsert_topic_preset(preset.model_dump(exclude_none=True))
    return TopicPreset.model_validate(saved)
