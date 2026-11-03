import urllib.request
import urllib.parse
import json
from typing import List
from models.scene_plan import MediaCandidate
from providers.base import BaseMediaProvider

class WikimediaProvider(BaseMediaProvider):
    """
    Adapter for Wikimedia Commons MediaSearch API for video content.
    No API key required.
    """

    SEARCH_URL = "https://commons.wikimedia.org/w/api.php"

    @property
    def name(self) -> str:
        return "wikimedia"

    def search(
        self,
        query: str,
        orientation: str = "landscape",
        per_page: int = 5,
        min_duration: float = 3.0,
        media_type: str = "all"
    ) -> List[MediaCandidate]:
        gsr = f"filetype:video {query}" if media_type == "video" else query
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": gsr,
            "gsrnamespace": "6",  # File namespace
            "gsrlimit": per_page,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata"
        }
        url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Drift-AI-Editor/1.0 (cutwire; drift-editor)"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        candidates: List[MediaCandidate] = []
        pages = data.get("query", {}).get("pages", {})
        for page_id, info in pages.items():
            imageinfo_list = info.get("imageinfo", [])
            if not imageinfo_list:
                continue
            img = imageinfo_list[0]
            file_url = img.get("url", "")
            is_vid = file_url.lower().endswith((".mp4", ".webm", ".ogv"))
            is_img = file_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
            if not is_vid and not is_img:
                continue

            metadata = img.get("extmetadata", {})
            license_short = metadata.get("LicenseShortName", {}).get("value", "Creative Commons / Public Domain")
            author = metadata.get("Artist", {}).get("value", "Wikimedia Contributor")
            
            # Clean author html tags if present
            author_clean = author.split("<")[0].strip() if "<" in author else author

            width = img.get("width", 1920)
            height = img.get("height", 1080)

            cand = MediaCandidate(
                platform="wikimedia",
                external_id=str(page_id),
                title=info.get("title", f"Wikimedia Video {page_id}"),
                preview_url=img.get("thumburl", ""),
                download_url=file_url,
                creator=author_clean or "Wikimedia Commons",
                page_url=img.get("descriptionurl", f"https://commons.wikimedia.org/?curid={page_id}"),
                license=f"Wikimedia Commons ({license_short})",
                width=width,
                height=height,
                duration=10.0,  # Default estimate for open media
                aspect_ratio="9:16" if height > width else "16:9"
            )
            candidates.append(cand)

        return candidates

