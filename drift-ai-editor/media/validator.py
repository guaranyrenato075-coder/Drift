import os
from pathlib import Path
from typing import Tuple

class MediaValidator:
    """
    Validates downloaded media files before timeline insertion.
    """

    SUPPORTED_VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
    SUPPORTED_AUDIO_EXTS = {".wav", ".mp3", ".aac", ".flac", ".ogg", ".m4a"}
    SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    @classmethod
    def validate_file(cls, file_path: Path | str, min_size_bytes: int = 1024) -> Tuple[bool, str]:
        path = Path(file_path)
        if not path.exists():
            return False, f"Arquivo não encontrado: {path}"

        if not path.is_file():
            return False, f"O caminho não é um arquivo: {path}"

        file_size = path.stat().st_size
        if file_size < min_size_bytes:
            return False, f"Arquivo corrompido ou incompleto (tamanho: {file_size} bytes)"

        suffix = path.suffix.lower()
        if (suffix not in cls.SUPPORTED_VIDEO_EXTS and 
            suffix not in cls.SUPPORTED_AUDIO_EXTS and 
            suffix not in cls.SUPPORTED_IMAGE_EXTS):
            return False, f"Formato de arquivo não suportado: {suffix}"

        return True, "Arquivo válido"

