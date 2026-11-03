import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class NasaProvider(BaseMediaProvider):
    """
    Adapter for NASA Image and Video Library (images.nasa.gov).
    Public domain science, space, planets, rocket and earth footage. No API key required.
    """

    SEARCH_URL = "https://images-api.nasa.gov/search"

    @property
    def name(self) -> str:
        return "nasa"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        nasa_mt = "image,video" if media_type == "all" else media_type
        params = {
            "q": query,
            "media_type": nasa_mt
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        items = data.get("collection", {}).get("items", [])[:per_page]

        for item in items:
            data_list = item.get("data", [])
            if not data_list:
                continue
            item_data = data_list[0]
            nasa_id = item_data.get("nasa_id", "")
            title = item_data.get("title", f"NASA Footage {nasa_id}")
            description = item_data.get("description", "")
            
            # Find preview thumbnail
            links = item.get("links", [])
            thumb_url = ""
            for l in links:
                if l.get("rel") == "preview":
                    thumb_url = l.get("href", "")
                    break

            # Collection manifest json link
            collection_url = item.get("href", "")
            download_url = ""

            # If collection url exists, query asset variants
            if collection_url:
                try:
                    c_req = urllib.request.Request(collection_url, headers={"User-Agent": "Drift-AI-Editor/1.0"})
                    with urllib.request.urlopen(c_req, timeout=5) as c_res:
                        assets = json.loads(c_res.read().decode("utf-8"))
                        # Find medium mp4
                        for a in assets:
                            if isinstance(a, str) and a.lower().endswith("~medium.mp4"):
                                download_url = a
                                break
                            elif isinstance(a, str) and a.lower().endswith(".mp4") and not download_url:
                                download_url = a
                except Exception:
                    pass

            cand = MediaCandidate(
                platform="nasa",
                external_id=nasa_id,
                title=title,
                preview_url=thumb_url,
                download_url=download_url,
                creator="NASA",
                page_url=f"https://images.nasa.gov/details/{nasa_id}",
                license="NASA Public Domain (Free for educational and informational use)",
                width=1920,
                height=1080,
                duration=15.0,
                aspect_ratio="16:9"
            )
            candidates.append(cand)

        return candidates

