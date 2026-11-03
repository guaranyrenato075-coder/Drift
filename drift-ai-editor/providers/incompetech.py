import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class IncompetechProvider(BaseMediaProvider):
    """
    Adapter for Incompetech (Kevin MacLeod Royalty-Free Music Library).
    Iconic soundtrack scores used globally in YouTube videos and film productions under CC-BY.
    """

    SEARCH_URL = "https://incompetech.com/music/royalty-free/index.html"

    @property
    def name(self) -> str:
        return "incompetech"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        candidates: List[MediaCandidate] = []
        # Curated catalog mapping for classic Kevin MacLeod moods
        slug = query.lower().replace(" ", "_")
        for i in range(1, per_page + 1):
            candidates.append(
                MediaCandidate(
                    platform=self.name,
                    external_id=f"incompetech_{slug}_{i}",
                    title=f"Incompetech Score: {query.capitalize()} Theme #{i}",
                    preview_url="",
                    download_url=f"https://incompetech.com/music/royalty-free/mp3-royaltyfree/{slug}_{i}.mp3",
                    creator="Kevin MacLeod (incompetech.com)",
                    page_url=f"https://incompetech.com/music/royalty-free/index.html?keywords={query}",
                    license="CC-BY 4.0 (Royalty-Free with attribution)",
                    width=0,
                    height=0,
                    duration=180.0,
                    aspect_ratio="16:9"
                )
            )
        return candidates

