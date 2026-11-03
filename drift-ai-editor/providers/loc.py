import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class LibraryOfCongressProvider(BaseMediaProvider):
    """
    Adapter for Library of Congress (LOC) API.
    Millions of public domain historical photographs, vintage prints, and documentary footage.
    No API key required.
    """

    SEARCH_URL = "https://www.loc.gov/search/"

    @property
    def name(self) -> str:
        return "loc"

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
            "fo": "json",
            "c": str(per_page),
            "fa": "online-format:image|online-format:video"
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
            image_urls = res.get("image_url", [])
            if not image_urls:
                continue

            img_url = image_urls[-1] if isinstance(image_urls, list) else str(image_urls)
            thumb_url = image_urls[0] if isinstance(image_urls, list) else img_url
            item_id = str(res.get("id", img_url))
            title = res.get("title", f"Library of Congress Item")
            author = res.get("contributor", ["Library of Congress"])[0] if res.get("contributor") else "Library of Congress"

            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=item_id,
                    title=title,
                    preview_url=thumb_url,
                    download_url=img_url,
                    creator=author,
                    page_url=res.get("url", img_url),
                    license="Public Domain - Library of Congress",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )

        return candidates
