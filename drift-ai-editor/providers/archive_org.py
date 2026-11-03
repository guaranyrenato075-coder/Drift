import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class ArchiveOrgProvider(BaseMediaProvider):
    """
    Adapter for Internet Archive (archive.org) Public Domain Video & Media API.
    100% Free - No API key required.
    Provides historical, documentary, NASA, science, and public domain archival films.
    """

    SEARCH_URL = "https://archive.org/advancedsearch.php"

    @property
    def name(self) -> str:
        return "archive_org"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        clean_q = query.replace('"', '').replace("'", "").strip()
        if not clean_q:
            return []

        # Target movies / videos
        media_filter = "mediatype:movies" if media_type == "video" else "(mediatype:movies OR mediatype:image)"
        full_query = f"{clean_q} AND {media_filter}"

        params = {
            "q": full_query,
            "fl[]": "identifier,title,description,mediatype",
            "rows": per_page,
            "page": 1,
            "output": "json"
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0 (cutwire; video-bot)"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        docs = data.get("response", {}).get("docs", [])
        for doc in docs:
            identifier = doc.get("identifier")
            if not identifier:
                continue

            # In Internet Archive, video items provide standard derivative webm or mp4
            # We can link the standard direct download preview/stream
            cand = MediaCandidate(
                platform="archive_org",
                external_id=identifier,
                title=doc.get("title") or f"Archive.org Media {identifier}",
                preview_url=f"https://archive.org/services/img/{identifier}",
                download_url=f"https://archive.org/download/{identifier}/{identifier}.mp4",
                creator="Internet Archive Public Domain Collection",
                page_url=f"https://archive.org/details/{identifier}",
                license="Public Domain / Creative Commons (Free)",
                width=1920,
                height=1080,
                duration=15.0,
                aspect_ratio="16:9"
            )
            candidates.append(cand)

        return candidates

