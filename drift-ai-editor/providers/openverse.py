import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class OpenverseProvider(BaseMediaProvider):
    """
    Adapter for Openverse (formerly CC Search by Creative Commons / WordPress Foundation).
    Indexes over 700 million Creative Commons and public domain images and audio.
    No API key required for public endpoint.
    """

    SEARCH_URL = "https://api.openverse.org/v1/images/"

    @property
    def name(self) -> str:
        return "openverse"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        aspect_ratio = "landscape" if orientation == "landscape" else "portrait"
        params = {
            "q": query,
            "page_size": str(per_page),
            "aspect_ratio": aspect_ratio
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        results = data.get("results", [])[:per_page]

        for item in results:
            img_url = item.get("url", "")
            if not img_url:
                continue

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=str(item.get("id", img_url)),
                    title=item.get("title", f"Openverse Image - {query}"),
                    preview_url=item.get("thumbnail", img_url),
                    download_url=img_url,
                    creator=item.get("creator", "Unknown Creator"),
                    page_url=item.get("foreign_landing_url", img_url),
                    license=item.get("license", "Creative Commons"),
                    width=item.get("width", 1920) or 1920,
                    height=item.get("height", 1080) or 1080,
                    duration=min_duration,
                    aspect_ratio="16:9" if orientation == "landscape" else "9:16"
                )
            )

        return candidates
