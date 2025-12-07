from __future__ import annotations

from typing import List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks

from ..schemas.models import DraftResponse, RunRequest, RunResponse, RunStatus
from ..services.supabase_service import supabase_service
from ..workflows.pipeline import pipeline

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/", response_model=RunResponse)
async def trigger_run(request: RunRequest, background_tasks: BackgroundTasks) -> RunResponse:
    run_id = str(uuid4())
    metadata = {
        "run_id": run_id,
        "title": request.title,
        "subject": request.subject,
        "preheader": request.preheader,
        "hero_query": request.hero_query or (request.topics[0] if request.topics else "news"),
        "rss_feeds": request.rss_feeds,
    }
    background_tasks.add_task(pipeline.run, request.topics, metadata)
    return RunResponse(run_id=run_id, status="queued")


@router.get("/", response_model=List[RunStatus])
def recent_runs() -> List[RunStatus]:
    runs = supabase_service.latest_runs()
    return [RunStatus.model_validate(item) for item in runs]


@router.get("/latest", response_model=DraftResponse | None)
def latest_draft() -> DraftResponse | None:
    latest = supabase_service.latest_draft()
    if not latest:
        return None
    return DraftResponse(
        run_id=latest.get("run_id", "unknown"),
        hero=latest.get("hero"),
        sections=latest.get("sections", []),
        html=latest.get("html", ""),
    )
