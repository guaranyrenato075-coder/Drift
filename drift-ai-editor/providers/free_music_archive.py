import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class FreeMusicArchiveProvider(BaseMediaProvider):
    """
    Adapter for Free Music Archive (FMA) / Royalty-Free Creative Commons tracks.
    """

    SEARCH_URL = "https://freemusicarchive.org/api/get/tracks.json"

    @property
    def name(self) -> str:
        return "free_music_archive"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "api_key": "demo",
            "q": query,
            "limit": str(per_page)
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        dataset = data.get("dataset", [])

        for item in dataset:
            track_url = item.get("track_file_url", "")
            if not track_url:
                continue

            item_id = str(item.get("track_id", track_url))
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=item.get("track_title", "Background Music Track"),
                    preview_url=item.get("track_image_file", ""),
                    download_url=track_url,
                    creator=item.get("artist_name", "FMA Artist"),
                    page_url=item.get("track_url", track_url),
                    license=item.get("license_title", "Creative Commons"),
                    width=0,
                    height=0,
                    duration=float(item.get("track_duration", 60.0) or 60.0),
                    aspect_ratio="16:9"
                )
            )

        return candidates
