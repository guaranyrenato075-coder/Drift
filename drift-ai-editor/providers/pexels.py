import urllib.request
import urllib.parse
import json
import os
from typing import List, Optional
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class PexelsProvider(BaseMediaProvider):
    """
    Adapter for Pexels official Video Search API.
    Uses PEXELS_API_KEY environment variable.
    """

    VIDEO_SEARCH_URL = "https://api.pexels.com/videos/search"
    PHOTO_SEARCH_URL = "https://api.pexels.com/v1/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("PEXELS_API_KEY", "")

    @property
    def name(self) -> str:
        return "pexels"

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

        ori_map = {"landscape": "landscape", "portrait": "portrait", "square": "square", "16:9": "landscape", "9:16": "portrait", "1:1": "square"}
        pexels_ori = ori_map.get(orientation, "landscape")
        candidates: List[MediaCandidate] = []

        headers = {"Authorization": self.api_key, "User-Agent": "Drift-AI-Editor/1.0"}

        # 1. Search Videos if requested
        if media_type in ("video", "all"):
            params = {"query": query, "orientation": pexels_ori, "per_page": per_page}
            url = f"{self.VIDEO_SEARCH_URL}?{urllib.parse.urlencode(params)}"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                for item in data.get("videos", []):
                    dur = float(item.get("duration", 0.0))
                    if dur > 0 and dur < min_duration:
                        continue
                    v_files = item.get("video_files", [])
                    sel = None
                    for vf in sorted(v_files, key=lambda x: (x.get("width") or 0), reverse=True):
                        if vf.get("file_type") == "video/mp4" and (vf.get("width") or 0) <= 1920:
                            sel = vf
                            break
                    if not sel and v_files:
                        sel = v_files[0]

                    cand = MediaCandidate(
                        platform="pexels",
                        media_type="video",
                        external_id=str(item.get("id")),
                        title=f"Pexels Vídeo {item.get('id')}",
                        preview_url=item.get("image", ""),
                        download_url=sel.get("link", "") if sel else "",
                        creator=item.get("user", {}).get("name", "Pexels Creator"),
                        page_url=item.get("url", ""),
                        license="Pexels License",
                        width=sel.get("width", 1920) if sel else 1920,
                        height=sel.get("height", 1080) if sel else 1080,
                        duration=dur,
                        aspect_ratio="9:16" if (sel.get("height", 1080) if sel else 1080) > (sel.get("width", 1920) if sel else 1920) else "16:9"
                    )
                    candidates.append(cand)
            except Exception:
                pass

        # 2. Search Photos if requested
        if media_type in ("image", "all") and len(candidates) < per_page:
            params = {"query": query, "orientation": pexels_ori, "per_page": per_page}
            url = f"{self.PHOTO_SEARCH_URL}?{urllib.parse.urlencode(params)}"
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                for item in data.get("photos", []):
                    src = item.get("src", {})
                    d_url = src.get("large2x") or src.get("original") or src.get("large") or ""
                    cand = MediaCandidate(
                        platform="pexels",
                        media_type="image",
                        external_id=str(item.get("id")),
                        title=f"Pexels Imagem {item.get('id')}",
                        preview_url=src.get("medium", d_url),
                        download_url=d_url,
                        creator=item.get("photographer", "Pexels Photographer"),
                        page_url=item.get("url", ""),
                        license="Pexels License",
                        width=item.get("width", 1920),
                        height=item.get("height", 1080),
                        duration=0.0,
                        aspect_ratio="9:16" if item.get("height", 1080) > item.get("width", 1920) else "16:9"
                    )
                    candidates.append(cand)
            except Exception:
                pass

        return candidates

