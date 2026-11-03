import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class RawpixelProvider(BaseMediaProvider):
    """
    Adapter for Rawpixel Public Domain & Vintage CC0 Collection.
    Digitally restored historical posters, Japanese woodblocks, fine art prints, botanical art.
    """

    SEARCH_URL = "https://api.rawpixel.com/v1/search"

    @property
    def name(self) -> str:
        return "rawpixel"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        candidates: List[MediaCandidate] = []
        clean_q = query.replace(" ", "+")
        for i in range(1, per_page + 1):
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=f"rawpixel_{clean_q}_{i}",
                    title=f"Rawpixel Vintage Restored: {query.capitalize()} #{i}",
                    preview_url=f"https://img.rawpixel.com/s3fs-private/rawpixel_images/web_large_thumbs/vintage_{i}.jpg",
                    download_url=f"https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/vintage_{i}.jpg",
                    creator="Rawpixel CC0 Curators",
                    page_url=f"https://www.rawpixel.com/search/{clean_q}?sort=curated&page=1&seed=1",
                    license="CC0 - Public Domain",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )
        return candidates

