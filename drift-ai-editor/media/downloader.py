import urllib.request
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from config import TEMP_DIR
from media.cache import MediaCache
from media.validator import MediaValidator
from models.scene_plan import MediaCandidate

class MediaDownloader:
    """
    Safely downloads media files to a temporary location, validates them,
    and moves them atomically into the persistent cache.
    """

    def __init__(self, cache: Optional[MediaCache] = None):
        self.cache = cache or MediaCache()

    def download_candidate(self, candidate: MediaCandidate, timeout_sec: int = 30) -> Tuple[bool, Optional[Path], str]:
        if not candidate.download_url:
            return False, None, "URL de download ausente para o clipe"

        # Check existing cache first
        url_lower = candidate.download_url.lower()
        if candidate.media_type == "image":
            if ".png" in url_lower:
                ext = ".png"
            elif ".webp" in url_lower:
                ext = ".webp"
            else:
                ext = ".jpg"
        else:
            if ".webm" in url_lower:
                ext = ".webm"
            else:
                ext = ".mp4"

        cached = self.cache.get_cached_file(candidate.platform, candidate.external_id, candidate.download_url, ext)
        if cached:
            candidate.local_cached_path = str(cached)
            return True, cached, "Obtido do cache local"

        target_path = self.cache.get_target_path(candidate.platform, candidate.external_id, candidate.download_url, ext)
        
        # Download to a temporary file first
        temp_fd, temp_path_str = tempfile.mkstemp(suffix=ext, dir=TEMP_DIR)
        temp_path = Path(temp_path_str)

        try:
            req = urllib.request.Request(
                candidate.download_url,
                headers={"User-Agent": "Drift-AI-Editor/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as response, open(temp_fd, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

            # Validate the temporary file
            valid, msg = MediaValidator.validate_file(temp_path)
            if not valid:
                temp_path.unlink(missing_ok=True)
                return False, None, f"Falha na validação do arquivo baixado: {msg}"

            # Atomically move to target cached path
            shutil.move(str(temp_path), str(target_path))
            candidate.local_cached_path = str(target_path)
            return True, target_path, "Download concluído com sucesso"

        except Exception as e:
            temp_path.unlink(missing_ok=True)
            return False, None, f"Erro durante o download: {str(e)}"

