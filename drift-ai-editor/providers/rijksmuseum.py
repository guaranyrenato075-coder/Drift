import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class RijksmuseumProvider(BaseMediaProvider):
    """
    Adapter for Rijksmuseum Amsterdam Open API.
    Over 700,000 Dutch Golden Age and world masterworks in ultra-high resolution.
    """

    SEARCH_URL = "https://www.rijksmuseum.nl/api/en/collection"

    @property
    def name(self) -> str:
        return "rijksmuseum"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "key": "2esrQLvR",  # Public demo educational key or registered key
            "q": query,
            "imgonly": "true",
            "ps": str(per_page)
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        art_objects = data.get("artObjects", [])

        for obj in art_objects:
            web_img = obj.get("webImage", {})
            img_url = web_img.get("url", "")
            if not img_url:
                continue

            obj_num = obj.get("objectNumber", "")
            title = obj.get("title", f"Rijksmuseum Artwork #{obj_num}")
            artist = obj.get("principalOrFirstMaker", "Rijksmuseum Artist")

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=obj_num,
                    title=title,
                    preview_url=img_url,
                    download_url=img_url,
                    creator=artist,
                    page_url=obj.get("links", {}).get("web", f"https://www.rijksmuseum.nl/en/collection/{obj_num}"),
                    license="CC0 - Public Domain",
                    width=web_img.get("width", 1920) or 1920,
                    height=web_img.get("height", 1080) or 1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates

