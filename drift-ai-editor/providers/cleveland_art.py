import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class ClevelandArtProvider(BaseMediaProvider):
    """
    Adapter for Cleveland Museum of Art Open Access API.
    Over 30,000 public domain art pieces. No API key required.
    """

    SEARCH_URL = "https://openaccess-api.clevelandart.org/api/artworks/"

    @property
    def name(self) -> str:
        return "cleveland_art"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "q": query,
            "has_image": "1",
            "cc0": "1",
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
        items = data.get("data", [])

        for it in items:
            images = it.get("images", {})
            web_img = images.get("web", {})
            img_url = web_img.get("url", "")
            if not img_url:
                continue

            item_id = str(it.get("id", ""))
            title = it.get("title", f"Cleveland Art #{item_id}")
            creators = it.get("creators", [])
            artist_name = creators[0].get("description", "Cleveland Art Master") if creators else "Cleveland Art Master"

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=title,
                    preview_url=img_url,
                    download_url=img_url,
                    creator=artist_name,
                    page_url=it.get("url", f"https://www.clevelandart.org/art/{item_id}"),
                    license="CC0 - Public Domain",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates

