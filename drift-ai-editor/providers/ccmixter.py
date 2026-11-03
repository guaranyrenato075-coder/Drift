import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class CcMixterProvider(BaseMediaProvider):
    """
    Adapter for ccMixter Community Music and Audio API.
    Thousands of open tracks, remixes, instrumentals under Creative Commons.
    """

    SEARCH_URL = "http://ccmixter.org/api/query"

    @property
    def name(self) -> str:
        return "ccmixter"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        params = {
            "f": "json",
            "search": query,
            "limit": str(per_page)
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        if isinstance(data, list):
            for it in data[:per_page]:
                files = it.get("files", [])
                download_url = files[0].get("download_url", "") if files else ""
                if not download_url:
                    continue

                item_id = str(it.get("upload_id", ""))
                candidates.append(
                    MediaCandidate(
                        platform=self.name,
                        external_id=item_id,
                        title=it.get("upload_name", f"ccMixter Track #{item_id}"),
                        preview_url="",
                        download_url=download_url,
                        creator=it.get("user_real_name", "ccMixter Artist"),
                        page_url=it.get("file_page_url", download_url),
                        license="Creative Commons (ccMixter)",
                        width=0,
                        height=0,
                        duration=float(it.get("upload_duration", 120.0) or 120.0),
                        aspect_ratio="16:9"
                    )
                )

        return candidates

