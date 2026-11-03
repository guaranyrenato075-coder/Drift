import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class WellcomeCollectionProvider(BaseMediaProvider):
    """
    Adapter for Wellcome Collection API (London).
    Historical medical illustrations, alchemy, rare manuscripts, and history of science.
    No API key required.
    """

    SEARCH_URL = "https://api.wellcomecollection.org/catalogue/v2/images"

    @property
    def name(self) -> str:
        return "wellcome_collection"

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
            "pageSize": str(per_page),
            "locations.license": "pdm,cc-0,cc-by"
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        results = data.get("results", [])

        for res in results:
            thumb = res.get("thumbnail", {})
            img_url = thumb.get("url", "")
            if not img_url:
                continue

            item_id = str(res.get("id", ""))
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=f"Wellcome Collection Record #{item_id}",
                    preview_url=img_url,
                    download_url=img_url,
                    creator="Wellcome Collection",
                    page_url=f"https://wellcomecollection.org/works/{item_id}",
                    license="Public Domain / CC-BY",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates

