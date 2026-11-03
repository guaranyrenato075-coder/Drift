# drift-ai-editor configuration
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
MEDIA_CACHE_DIR = BASE_DIR / "media_cache"
TEMP_DIR = BASE_DIR / "temp"

for directory in (STORAGE_DIR, MEDIA_CACHE_DIR, TEMP_DIR):
    directory.mkdir(parents=True, exist_ok=True)

DB_PATH = STORAGE_DIR / "projects.db"

