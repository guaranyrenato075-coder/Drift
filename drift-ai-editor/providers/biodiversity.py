import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class BiodiversityProvider(BaseMediaProvider):
    """
    Adapter for Biodiversity Heritage Library (BHL) API.
    Over 150,000 biological illustrations, flora, fauna, botanical prints in public domain.
    """

    SEARCH_URL = "https://www.biodiversitylibrary.org/api3"

    @property
    def name(self) -> str:
        return "biodiversity"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "op": "PublicationSearch",
            "searchterm": query,
            "format": "json",
            "apikey": "demo"
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        results = data.get("Result", [])[:per_page]

        for it in results:
            title_id = str(it.get("TitleID", ""))
            if not title_id:
                continue

            thumb_url = f"https://www.biodiversitylibrary.org/pagethumb/{title_id},500,500"
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=title_id,
                    title=it.get("FullTitle", f"BHL Specimen #{title_id}"),
                    preview_url=thumb_url,
                    download_url=thumb_url,
                    creator=it.get("Authors", "Biodiversity Heritage Library"),
                    page_url=it.get("TitleUrl", f"https://www.biodiversitylibrary.org/bibliography/{title_id}"),
                    license="Public Domain - Biodiversity Heritage Library",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates

