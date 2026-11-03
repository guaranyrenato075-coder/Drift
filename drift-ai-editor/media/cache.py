import hashlib
from pathlib import Path
from typing import Optional
from config import MEDIA_CACHE_DIR

class MediaCache:
    """
    Manages local filesystem caching of downloaded stock video assets.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or MEDIA_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, platform: str, external_id: str, download_url: str) -> str:
        raw = f"{platform}:{external_id}:{download_url}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def get_cached_file(self, platform: str, external_id: str, download_url: str, ext: str = ".mp4") -> Optional[Path]:
        key = self.get_cache_key(platform, external_id, download_url)
        expected_path = self.cache_dir / f"{platform}_{key}{ext}"
        if expected_path.exists() and expected_path.stat().st_size > 1024:
            return expected_path
        return None

    def get_target_path(self, platform: str, external_id: str, download_url: str, ext: str = ".mp4") -> Path:
        key = self.get_cache_key(platform, external_id, download_url)
        return self.cache_dir / f"{platform}_{key}{ext}"

