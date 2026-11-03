import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from models.scene_plan import MediaCandidate

class LocalMediaIndexer:
    """
    Scans, catalogs, and indexes personal local directories containing video clips
    and images. Extracts keywords from file names, directory structures, and metadata,
    allowing the AI editor to search and prioritize local assets before calling online APIs.
    """

    SUPPORTED_VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
    SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff"}

    def __init__(self, index_cache_path: Optional[Path] = None):
        if index_cache_path is None:
            index_cache_path = Path(__file__).resolve().parent.parent / "storage" / "local_index.json"
        self.index_cache_path = Path(index_cache_path)
        self.index_cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.catalog: List[Dict[str, Any]] = []
        self._load_index()

    def _load_index(self):
        if self.index_cache_path.exists():
            try:
                import json
                with open(self.index_cache_path, "r", encoding="utf-8") as f:
                    self.catalog = json.load(f)
            except Exception:
                self.catalog = []

    def _save_index(self):
        import json
        with open(self.index_cache_path, "w", encoding="utf-8") as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)

    def scan_directory(self, folder_path: str) -> int:
        """
        Recursively indexes a directory of user assets.
        Returns number of newly indexed files.
        """
        root = Path(folder_path)
        if not root.exists() or not root.is_dir():
            return 0

        new_count = 0
        existing_paths = {item["path"] for item in self.catalog}

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            if ext not in self.SUPPORTED_VIDEO_EXTS and ext not in self.SUPPORTED_IMAGE_EXTS:
                continue

            str_path = str(path.resolve())
            if str_path in existing_paths:
                continue

            # Extract semantic tokens from filename and parent folder
            clean_name = re.sub(r"[-_.]+", " ", path.stem).lower()
            parent_name = re.sub(r"[-_.]+", " ", path.parent.name).lower()
            keywords = list(set(clean_name.split() + parent_name.split()))

            is_video = ext in self.SUPPORTED_VIDEO_EXTS
            size_mb = round(path.stat().st_size / (1024 * 1024), 2)

            entry = {
                "path": str_path,
                "filename": path.name,
                "keywords": keywords,
                "type": "video" if is_video else "image",
                "extension": ext,
                "size_mb": size_mb,
                "parent_folder": path.parent.name
            }
            self.catalog.append(entry)
            new_count += 1

        if new_count > 0:
            self._save_index()

        return new_count

    def search_local(
        self,
        query: str,
        media_type: str = "all",
        limit: int = 5
    ) -> List[MediaCandidate]:
        """Searches indexed personal assets by query terms."""
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        if not query_terms:
            return []

        scored_matches = []
        for item in self.catalog:
            if media_type != "all" and item["type"] != media_type:
                continue

            item_keywords = item.get("keywords", [])
            match_score = sum(2 if term in item_keywords else (1 if term in item["filename"].lower() else 0) for term in query_terms)
            if match_score > 0:
                scored_matches.append((match_score, item))

        scored_matches.sort(key=lambda x: x[0], reverse=True)

        candidates: List[MediaCandidate] = []
        for score, item in scored_matches[:limit]:
            cand = MediaCandidate(
                platform="local",
                external_id=Path(item["path"]).stem,
                title=f"Local: {item['filename']}",
                preview_url=item["path"],
                download_url=item["path"],
                local_cached_path=item["path"],
                creator="Biblioteca Pessoal",
                page_url=f"file:///{item['path']}",
                license="Acervo Pessoal (Uso Próprio)",
                width=1920,
                height=1080,
                duration=10.0 if item["type"] == "video" else 5.0,
                aspect_ratio="16:9"
            )
            candidates.append(cand)

        return candidates

