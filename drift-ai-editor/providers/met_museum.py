import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class MetMuseumProvider(BaseMediaProvider):
    """
    Adapter for The Metropolitan Museum of Art Collection API.
    Provides over 400,000 public domain (CC0) high-resolution artworks.
    No API key required.
    """

    SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

    @property
    def name(self) -> str:
        return "met_museum"

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
            "hasImages": "true",
            "isPublicDomain": "true"
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        object_ids = data.get("objectIDs", []) or []
        target_ids = object_ids[:min(per_page, 4)]
        candidates: List[MediaCandidate] = []

        for oid in target_ids:
            obj_req = urllib.request.Request(f"{self.OBJECT_URL}{oid}", headers={"User-Agent": "Drift-AI-Editor/1.0"})
            try:
                with urllib.request.urlopen(obj_req, timeout=5) as resp:
                    obj = json.loads(resp.read().decode("utf-8"))
                    primary_img = obj.get("primaryImage", "")
                    if not primary_img:
                        primary_img = obj.get("primaryImageSmall", "")
                    if not primary_img:
                        continue

                    artist = obj.get("artistDisplayName") or "The Met Open Access"
                    title = obj.get("title") or f"Artwork #{oid}"

                    candidates.append(
                        MediaCandidate(
                            platform=self.name,
                            external_id=str(oid),
                            title=title,
                            preview_url=obj.get("primaryImageSmall", primary_img),
                            download_url=primary_img,
                            creator=artist,
                            page_url=f"https://www.metmuseum.org/art/collection/search/{oid}",
                            license="CC0 - Public Domain",
                            width=1920,
                            height=1080,
                            duration=min_duration,
                            aspect_ratio="16:9"
                        )
                    )
            except Exception:
                continue

        return candidates
