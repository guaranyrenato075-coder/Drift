import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class SmithsonianProvider(BaseMediaProvider):
    """
    Adapter for Smithsonian Open Access API.
    Over 4.5 million 2D and 3D CC0 public domain cultural and scientific assets.
    """

    SEARCH_URL = "https://api.si.edu/openaccess/api/v1.0/search"

    @property
    def name(self) -> str:
        return "smithsonian"

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
            "rows": str(per_page),
            "api_key": "DEMO_KEY"
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        rows = data.get("response", {}).get("rows", [])

        for r in rows:
            content = r.get("content", {})
            descriptive = content.get("descriptiveNonRepeating", {})
            media_list = descriptive.get("online_media", {}).get("media", [])
            if not media_list:
                continue

            first_media = media_list[0]
            resource_url = first_media.get("content", "")
            if not resource_url:
                continue

            thumb_url = first_media.get("thumbnail", resource_url)
            item_id = str(r.get("id", ""))
            title = r.get("title", f"Smithsonian Item {item_id}")

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=title,
                    preview_url=thumb_url,
                    download_url=resource_url,
                    creator="Smithsonian Institution",
                    page_url=f"https://www.si.edu/object/{item_id}",
                    license="CC0 - Smithsonian Open Access",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates
