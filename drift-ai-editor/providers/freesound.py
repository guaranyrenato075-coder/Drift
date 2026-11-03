import urllib.request
import urllib.parse
import json
import os
from typing import List, Optional
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class FreesoundProvider(BaseMediaProvider):
    """
    Adapter for Freesound.org Audio API.
    Uses FREESOUND_API_KEY environment variable.
    Provides sound effects (SFX), foley, and ambient audio tracks.
    """

    SEARCH_URL = "https://freesound.org/apiv2/search/text/"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("FREESOUND_API_KEY", "")

    @property
    def name(self) -> str:
        return "freesound"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        if not self.api_key:
            return []

        params = {
            "query": query,
            "page_size": per_page,
            "fields": "id,name,previews,username,license,duration,url",
            "token": self.api_key
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        headers = {"User-Agent": "Drift-AI-Editor/1.0"}

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        for item in data.get("results", []):
            sound_id = str(item.get("id"))
            previews = item.get("previews", {})
            download_url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
            if not download_url:
                continue

            candidates.append(
                MediaCandidate(
                    platform="freesound",
                    external_id=sound_id,
                    title=item.get("name") or f"Sound {sound_id}",
                    preview_url=download_url,
                    download_url=download_url,
                    creator=item.get("username") or "Freesound User",
                    page_url=item.get("url") or f"https://freesound.org/s/{sound_id}/",
                    license=item.get("license") or "Creative Commons",
                    width=0,
                    height=0,
                    duration=float(item.get("duration", 5.0)),
                    aspect_ratio="audio"
                )
            )

        return candidates

