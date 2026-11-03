import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class MixkitProvider(BaseMediaProvider):
    """
    Adapter for Mixkit (Free Stock Video Footage & Sound Effects by Envato).
    """

    SEARCH_URL = "https://mixkit.co/api/v1/search"

    @property
    def name(self) -> str:
        return "mixkit"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "query": query,
            "type": "video" if media_type == "video" else "all",
            "page_size": str(per_page)
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        items = data.get("data", [])

        for it in items:
            v_url = it.get("video_url", "")
            if not v_url:
                v_url = it.get("download_url", "")
            if not v_url:
                continue

            item_id = str(it.get("id", v_url))
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=it.get("title", f"Mixkit Stock Video - {query}"),
                    preview_url=it.get("thumbnail_url", ""),
                    download_url=v_url,
                    creator="Mixkit Creator",
                    page_url=it.get("page_url", v_url),
                    license="Mixkit Free Stock Video License",
                    width=1920,
                    height=1080,
                    duration=float(it.get("duration", 8.0) or 8.0),
                    aspect_ratio="16:9"
                )
            )

        return candidates
