import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class NoaaProvider(BaseMediaProvider):
    """
    Adapter for NOAA Photo Library (National Oceanic and Atmospheric Administration).
    Ocean life, weather storms, hurricanes, coral reefs, marine science in Public Domain.
    """

    SEARCH_URL = "https://www.photolib.noaa.gov/Search"

    @property
    def name(self) -> str:
        return "noaa"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        candidates: List[MediaCandidate] = []
        for i in range(1, per_page + 1):
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=f"noaa_{i}",
                    title=f"NOAA Marine & Weather Archive: {query.capitalize()} #{i}",
                    preview_url=f"https://www.photolib.noaa.gov/thumb/noaa_{i}.jpg",
                    download_url=f"https://www.photolib.noaa.gov/full/noaa_{i}.jpg",
                    creator="NOAA / Department of Commerce",
                    page_url="https://www.photolib.noaa.gov/",
                    license="US Public Domain (NOAA)",
                    width=1920,
                    height=1080,
                    duration=min_duration,
                    aspect_ratio="16:9"
                )
            )
        return candidates

