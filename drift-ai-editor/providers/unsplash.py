import urllib.request
import urllib.parse
import json
import os
from typing import List, Optional
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class UnsplashProvider(BaseMediaProvider):
    """
    Adapter for Unsplash Photo Search API.
    Uses UNSPLASH_ACCESS_KEY environment variable.
    Provides cinematic, high-resolution photography with attribution.
    """

    SEARCH_URL = "https://api.unsplash.com/search/photos"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("UNSPLASH_ACCESS_KEY", "")

    @property
    def name(self) -> str:
        return "unsplash"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        # Unsplash is photography (images)
        if media_type == "video":
            return []

        if not self.api_key:
            return []

        ori_map = {
            "landscape": "landscape",
            "portrait": "portrait",
            "square": "squarish",
            "16:9": "landscape",
            "9:16": "portrait",
            "1:1": "squarish"
        }
        params = {
            "query": query,
            "orientation": ori_map.get(orientation, "landscape"),
            "per_page": per_page
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        headers = {
            "Authorization": f"Client-ID {self.api_key}",
            "User-Agent": "Drift-AI-Editor/1.0"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        for item in data.get("results", []):
            photo_id = str(item.get("id"))
            urls = item.get("urls", {})
            download_url = urls.get("regular") or urls.get("full") or urls.get("raw")
            if not download_url:
                continue

            user = item.get("user", {})
            creator = user.get("name") or user.get("username") or "Unsplash Photographer"
            user_url = user.get("links", {}).get("html", "https://unsplash.com")

            candidates.append(
                MediaCandidate(
                    platform="unsplash",
                    external_id=photo_id,
                    title=item.get("alt_description") or f"Unsplash Photo {photo_id}",
                    preview_url=urls.get("small", download_url),
                    download_url=download_url,
                    creator=creator,
                    page_url=item.get("links", {}).get("html", f"https://unsplash.com/photos/{photo_id}"),
                    license="Unsplash License (Free commercial & personal use)",
                    width=item.get("width", 1920),
                    height=item.get("height", 1080),
                    duration=min_duration,
                    aspect_ratio="9:16" if item.get("height", 1080) > item.get("width", 1920) else "16:9"
                )
            )

        return candidates

