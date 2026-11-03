import urllib.request
import urllib.parse
import json
import os
from typing import List, Optional
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class CoverrProvider(BaseMediaProvider):
    """
    Adapter for Coverr.co Video API.
    Uses COVERR_API_KEY environment variable.
    Provides free HD/4K stock video footage for commercial and personal use.
    """

    SEARCH_URL = "https://api.coverr.co/videos"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("COVERR_API_KEY", "")

    @property
    def name(self) -> str:
        return "coverr"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        # Coverr is exclusively video footage
        if media_type == "image":
            return []

        if not self.api_key:
            return []

        params = {
            "query": query,
            "page_size": per_page
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Drift-AI-Editor/1.0"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        hits = data.get("hits", []) or data.get("videos", [])
        for item in hits:
            vid_id = str(item.get("id"))
            urls = item.get("urls", {})
            download_url = urls.get("mp4") or urls.get("mp4_download") or item.get("download_url")
            if not download_url:
                continue

            candidates.append(
                MediaCandidate(
                    platform="coverr",
                    external_id=vid_id,
                    title=item.get("title") or f"Coverr Video {vid_id}",
                    preview_url=urls.get("thumbnail") or item.get("thumbnail_url", ""),
                    download_url=download_url,
                    creator=item.get("author", {}).get("name") or "Coverr Creator",
                    page_url=f"https://coverr.co/videos/{vid_id}",
                    license="Coverr Free License (Free commercial & personal use)",
                    width=item.get("width", 1920),
                    height=item.get("height", 1080),
                    duration=float(item.get("duration", 10.0)),
                    aspect_ratio="16:9"
                )
            )

        return candidates

