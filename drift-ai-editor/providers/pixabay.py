import urllib.request
import urllib.parse
import json
import os
from typing import List, Optional
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class PixabayProvider(BaseMediaProvider):
    """
    Adapter for Pixabay official Videos API.
    Uses PIXABAY_API_KEY environment variable.
    """

    VIDEO_SEARCH_URL = "https://pixabay.com/api/videos/"
    IMAGE_SEARCH_URL = "https://pixabay.com/api/"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("PIXABAY_API_KEY", "")

    @property
    def name(self) -> str:
        return "pixabay"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        if not self.api_key:
            return []

        candidates: List[MediaCandidate] = []

        # 1. Search Videos
        if media_type in ("video", "all"):
            params = {
                "key": self.api_key,
                "q": query,
                "per_page": per_page,
                "video_type": "film"
            }
            url = f"{self.VIDEO_SEARCH_URL}?{urllib.parse.urlencode(params)}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                for hit in data.get("hits", []):
                    dur = float(hit.get("duration", 0.0))
                    if dur > 0 and dur < min_duration:
                        continue
                    v_dict = hit.get("videos", {})
                    v_info = v_dict.get("large") or v_dict.get("medium") or v_dict.get("small", {})
                    cand = MediaCandidate(
                        platform="pixabay",
                        media_type="video",
                        external_id=str(hit.get("id")),
                        title=f"Pixabay Vídeo {hit.get('tags', '')}",
                        preview_url=hit.get("userImageURL") or v_info.get("thumbnail", ""),
                        download_url=v_info.get("url", ""),
                        creator=hit.get("user", "Pixabay Creator"),
                        page_url=hit.get("pageURL", ""),
                        license="Pixabay Content License",
                        width=v_info.get("width", 1920),
                        height=v_info.get("height", 1080),
                        duration=dur,
                        aspect_ratio="9:16" if v_info.get("height", 1080) > v_info.get("width", 1920) else "16:9"
                    )
                    candidates.append(cand)
            except Exception:
                pass

        # 2. Search Images
        if media_type in ("image", "all") and len(candidates) < per_page:
            params = {
                "key": self.api_key,
                "q": query,
                "per_page": per_page,
                "image_type": "photo"
            }
            url = f"{self.IMAGE_SEARCH_URL}?{urllib.parse.urlencode(params)}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                for hit in data.get("hits", []):
                    cand = MediaCandidate(
                        platform="pixabay",
                        media_type="image",
                        external_id=str(hit.get("id")),
                        title=f"Pixabay Imagem {hit.get('tags', '')}",
                        preview_url=hit.get("webformatURL", ""),
                        download_url=hit.get("largeImageURL", hit.get("webformatURL", "")),
                        creator=hit.get("user", "Pixabay Photographer"),
                        page_url=hit.get("pageURL", ""),
                        license="Pixabay Content License",
                        width=hit.get("imageWidth", 1920),
                        height=hit.get("imageHeight", 1080),
                        duration=0.0,
                        aspect_ratio="9:16" if hit.get("imageHeight", 1080) > hit.get("imageWidth", 1920) else "16:9"
                    )
                    candidates.append(cand)
            except Exception:
                pass

        return candidates

