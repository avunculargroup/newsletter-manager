"""Supabase wrapper used by the API layer and the Celery workflows."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover - optional dependency during tests
    Client = None  # type: ignore
    create_client = None  # type: ignore

from ..config import get_settings
from ..logger import get_logger

logger = get_logger(__name__)


@dataclass
class InMemoryStore:
    """Fallback store when Supabase credentials are not configured."""

    topic_presets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    runs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    drafts: List[Dict[str, Any]] = field(default_factory=list)


class SupabaseService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[Client] = None
        self._memory = InMemoryStore()

        if self.settings.supabase_url and self.settings.supabase_service_role_key:
            if create_client is None:
                raise RuntimeError(
                    "supabase package is not installed but SUPABASE_URL/KEY are configured"
                )
            self._client = create_client(
                str(self.settings.supabase_url), self.settings.supabase_service_role_key
            )
            logger.info("supabase_client.initialised", url=str(self.settings.supabase_url))
        else:
            logger.warning("supabase_client.memory_fallback")

    # ------------------------------------------------------------------
    # Topics
    # ------------------------------------------------------------------
    def list_topic_presets(self) -> List[Dict[str, Any]]:
        if self._client:
            response = self._client.table("topic_presets").select("*").execute()
            return response.data or []
        return list(self._memory.topic_presets.values())

    def upsert_topic_preset(self, preset: Dict[str, Any]) -> Dict[str, Any]:
        preset.setdefault("id", preset.get("slug"))
        preset.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
        if self._client:
            response = self._client.table("topic_presets").upsert(preset).execute()
            return response.data[0]
        self._memory.topic_presets[preset["id"]] = preset
        return preset

    # ------------------------------------------------------------------
    # Runs
    # ------------------------------------------------------------------
    def record_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload.setdefault("id", payload.get("run_id"))
        payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        if self._client:
            response = self._client.table("runs").insert(payload).execute()
            return response.data[0]
        self._memory.runs[payload["id"]] = payload
        return payload

    def update_run_status(self, run_id: str, status: str, message: str = "") -> None:
        update = {"status": status, "message": message}
        if self._client:
            self._client.table("runs").update(update).eq("id", run_id).execute()
            return
        if run_id in self._memory.runs:
            self._memory.runs[run_id].update(update)

    def latest_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        if self._client:
            response = (
                self._client.table("runs")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        runs = list(self._memory.runs.values())
        return sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True)[:limit]

    # ------------------------------------------------------------------
    # Drafts
    # ------------------------------------------------------------------
    def save_draft_sections(
        self,
        run_id: str,
        sections: List[Dict[str, Any]],
        html: str,
        hero: Optional[Dict[str, Any]],
    ) -> None:
        entry = {
            "run_id": run_id,
            "sections": sections,
            "html": html,
            "hero": hero,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if self._client:
            self._client.table("draft_sections").insert(entry).execute()
            return
        self._memory.drafts.append(entry)

    def latest_draft(self) -> Optional[Dict[str, Any]]:
        if self._client:
            response = (
                self._client.table("draft_sections")
                .select("*")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            data = response.data or []
            return data[0] if data else None
        return self._memory.drafts[-1] if self._memory.drafts else None


supabase_service = SupabaseService()
