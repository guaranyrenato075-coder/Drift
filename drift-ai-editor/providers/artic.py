import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class ArtInstituteChicagoProvider(BaseMediaProvider):
    """
    Adapter for Art Institute of Chicago API.
    Public domain masterworks and fine art. No API key required.
    """

    SEARCH_URL = "https://api.artic.edu/api/v1/artworks/search"
    IIIF_BASE_URL = "https://www.artic.edu/iiif/2"

    @property
    def name(self) -> str:
        return "artic"

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
            "fields": "id,title,image_id,artist_display,is_public_domain",
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

        for item in items:
            image_id = item.get("image_id")
            if not image_id:
                continue

            full_img = f"{self.IIIF_BASE_URL}/{image_id}/full/843,/0/default.jpg"
            thumb_img = f"{self.IIIF_BASE_URL}/{image_id}/full/400,/0/default.jpg"
            item_id = str(item.get("id", ""))

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=item.get("title", f"Art Institute of Chicago #{item_id}"),
                    preview_url=thumb_img,
                    download_url=full_img,
                    creator=item.get("artist_display", "Unknown Artist"),
                    page_url=f"https://www.artic.edu/artworks/{item_id}",
                    license="CC0 - Public Domain",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates
