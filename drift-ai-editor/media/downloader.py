import os
import urllib.request
import urllib.parse
import ipaddress
import socket
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
    Includes defense-in-depth anti-SSRF validation.
    """

    @staticmethod
    def is_safe_download_url(url: str) -> Tuple[bool, str]:
        """
        Validates URL scheme and destination to prevent SSRF and local file leaks.
        """
        if not url or not isinstance(url, str):
            return False, "URL vazia ou inválida"
        
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False, f"Protocolo não permitido: '{parsed.scheme}'. Apenas http e https são autorizados."

        hostname = parsed.hostname
        if not hostname:
            return False, "Hostname ausente na URL"

        hostname_lower = hostname.lower()
        if hostname_lower in ("localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "metadata.google.internal"):
            return False, f"Acesso bloqueado a endereço reservado ou interno: '{hostname}'"

        try:
            # Tenta verificar se o hostname é um IP literal
            ip = ipaddress.ip_address(hostname_lower)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False, f"Acesso bloqueado a endereço IP não público: {ip}"
        except ValueError:
            # Hostname com domínio de texto (ex: images.pexels.com), permitido
            pass

        return True, "URL segura"

    def __init__(self, cache: Optional[MediaCache] = None):
        self.cache = cache or MediaCache()

    def download_candidate(self, candidate: MediaCandidate, timeout_sec: int = 30) -> Tuple[bool, Optional[Path], str]:
        if candidate.local_cached_path and os.path.exists(candidate.local_cached_path):
            return True, Path(candidate.local_cached_path), "Arquivo local já existente"

        if not candidate.download_url:
            return False, None, "URL de download ausente para o clipe"

        # Anti-SSRF Security Validation
        is_safe, sec_reason = self.is_safe_download_url(candidate.download_url)
        if not is_safe:
            return False, None, f"Bloqueio de segurança (SSRF): {sec_reason}"

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
        
        # Download to a temporary file first (safely closing fd for Windows file lock compatibility)
        temp_fd, temp_path_str = tempfile.mkstemp(suffix=ext, dir=TEMP_DIR)
        os.close(temp_fd)
        temp_path = Path(temp_path_str)

        try:
            import ssl
            ssl_ctx = ssl._create_unverified_context()
            req = urllib.request.Request(
                candidate.download_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "*/*"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout_sec, context=ssl_ctx) as response, open(temp_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)

            # Validate the temporary file
            valid, msg = MediaValidator.validate_file(temp_path)
            if not valid:
                try:
                    if temp_path.exists():
                        temp_path.unlink()
                except Exception:
                    pass
                return False, None, f"Falha na validação do arquivo baixado: {msg}"

            # Atomically move to target cached path
            shutil.move(str(temp_path), str(target_path))
            candidate.local_cached_path = str(target_path)
            return True, target_path, "Download concluído com sucesso"

        except Exception as e:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception:
                pass
            return False, None, f"Erro durante o download: {str(e)}"

