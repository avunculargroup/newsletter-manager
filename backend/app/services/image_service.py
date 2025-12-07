"""Image search helpers (Unsplash + optional generative fallback)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import httpx

from ..config import get_settings
from ..logger import get_logger

logger = get_logger(__name__)


@dataclass
class ImageAsset:
    url: str
    thumb_url: str
    photographer: str
    unsplash_link: str
    attribution: str


class ImageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.http = httpx.Client(timeout=20.0)

    def fetch(self, query: str) -> Optional[ImageAsset]:
        if not self.settings.unsplash_access_key:
            logger.warning("image.unsplash.disabled", reason="missing UNSPLASH_ACCESS_KEY")
            return None

        params = {"query": query, "per_page": 1}
        response = self.http.get(
            "https://api.unsplash.com/search/photos",
            params=params,
            headers={"Authorization": f"Client-ID {self.settings.unsplash_access_key}"},
        )
        if response.status_code >= 400:
            logger.error(
                "image.unsplash.error",
                status=response.status_code,
                body=response.text,
                query=query,
            )
            return None
        data = response.json()
        results: List[dict] = data.get("results", [])
        if not results:
            return None
        photo = results[0]
        user = photo.get("user", {})
        attribution = f"Photo by {user.get('name')} on Unsplash"
        return ImageAsset(
            url=photo["urls"]["regular"],
            thumb_url=photo["urls"].get("thumb", photo["urls"].get("small")),
            photographer=user.get("name", "Unknown"),
            unsplash_link=photo.get("links", {}).get("html", photo.get("links", {}).get("self", "")),
            attribution=attribution,
        )


image_service = ImageService()
