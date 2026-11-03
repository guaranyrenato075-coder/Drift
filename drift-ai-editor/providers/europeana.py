import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class EuropeanaProvider(BaseMediaProvider):
    """
    Adapter for Europeana API.
    Over 50 million digitized cultural heritage items from European museums, galleries, and archives.
    """

    SEARCH_URL = "https://api.europeana.eu/record/v2/search.json"

    @property
    def name(self) -> str:
        return "europeana"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        media_filter = "IMAGE" if media_type == "image" else ("VIDEO" if media_type == "video" else "")
        params = {
            "wskey": "api2demo",
            "query": query,
            "rows": str(per_page),
            "reusability": "open"
        }
        if media_filter:
            params["qf"] = f"TYPE:{media_filter}"

        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        items = data.get("items", [])

        for it in items:
            edmPreview = it.get("edmPreview", [])
            img_url = edmPreview[0] if isinstance(edmPreview, list) and edmPreview else ""
            if not img_url:
                continue

            item_id = str(it.get("id", img_url))
            title = it.get("title", [f"Europeana Record"])[0] if it.get("title") else "Europeana Heritage Asset"
            provider_org = it.get("dataProvider", ["Europeana Contributor"])[0] if it.get("dataProvider") else "Europeana"

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=title,
                    preview_url=img_url,
                    download_url=img_url,
                    creator=provider_org,
                    page_url=f"https://www.europeana.eu/item/{item_id}",
                    license="Europeana Open Reusable",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates
