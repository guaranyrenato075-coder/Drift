import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class JamendoMusicProvider(BaseMediaProvider):
    """
    Adapter for Jamendo Music API.
    Over 600,000 royalty-free tracks under Creative Commons from indie artists worldwide.
    """

    SEARCH_URL = "https://api.jamendo.com/v3.0/tracks"

    @property
    def name(self) -> str:
        return "jamendo"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "client_id": "56d30c95",  # Jamendo Public Developer demo client
            "format": "json",
            "limit": str(per_page),
            "search": query,
            "include": "musicinfo"
        }
        url = f"{self.SEARCH_URL}/?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        results = data.get("results", [])

        for r in results:
            audio_url = r.get("audio", "")
            if not audio_url:
                continue

            track_id = str(r.get("id", ""))
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=track_id,
                    title=r.get("name", f"Jamendo Track #{track_id}"),
                    preview_url=r.get("image", ""),
                    download_url=audio_url,
                    creator=r.get("artist_name", "Jamendo Artist"),
                    page_url=r.get("shareurl", audio_url),
                    license="Creative Commons (Jamendo Free License)",
                    width=0,
                    height=0,
                    duration=float(r.get("duration", 180.0) or 180.0),
                    aspect_ratio="16:9"
                )
            )

        return candidates

