import sqlite3
import json
import time
import base64
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Generator
from contextlib import contextmanager
from models.scene_plan import ProjectPlan
from config import DB_PATH

@dataclass
class CursorPage:
    items: List[Dict[str, Any]]
    next_cursor: Optional[str]
    has_more: bool
    limit: int

class ProjectRepository:
    """
    Manages persistent storage of AI Editor projects and scene plans in SQLite.
    Optimized with WAL mode, surgical indexes, and cursor-based pagination.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        # High performance PRAGMAs: WAL mode, memory temp store, 32MB cache
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA cache_size = -32000;")
            conn.execute("PRAGMA temp_store = MEMORY;")
        except Exception:
            pass
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    scene_count INTEGER NOT NULL,
                    total_duration REAL NOT NULL,
                    raw_script TEXT,
                    plan_data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            # Surgical indexing: composite cursor index and search indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_cursor ON projects(updated_at DESC, project_id DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_projects_title ON projects(title)")
            conn.commit()

    def save(self, plan: ProjectPlan) -> None:
        plan.updated_at = time.time()
        plan_json = json.dumps(plan.to_dict(), ensure_ascii=False)
        total_dur = plan.total_duration()
        scene_count = len(plan.scenes)

        with self._connection() as conn:
            conn.execute("""
                INSERT INTO projects (project_id, title, scene_count, total_duration, raw_script, plan_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    title = excluded.title,
                    scene_count = excluded.scene_count,
                    total_duration = excluded.total_duration,
                    raw_script = excluded.raw_script,
                    plan_data = excluded.plan_data,
                    updated_at = excluded.updated_at
            """, (
                plan.project_id,
                plan.title,
                scene_count,
                total_dur,
                plan.raw_script,
                plan_json,
                plan.created_at,
                plan.updated_at
            ))
            conn.commit()

    def get(self, project_id: str) -> Optional[ProjectPlan]:
        with self._connection() as conn:
            cursor = conn.execute("SELECT plan_data FROM projects WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = json.loads(row["plan_data"])
            return ProjectPlan.from_dict(data)

    def list_all(self) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            cursor = conn.execute("""
                SELECT project_id, title, scene_count, total_duration, created_at, updated_at
                FROM projects ORDER BY updated_at DESC, project_id DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def encode_cursor(updated_at: float, project_id: str) -> str:
        payload = f"{updated_at}:{project_id}"
        return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode_cursor(cursor_str: str) -> tuple[float, str]:
        raw = base64.urlsafe_b64decode(cursor_str.encode("utf-8")).decode("utf-8")
        parts = raw.split(":", 1)
        return float(parts[0]), parts[1]

    def list_cursor(self, limit: int = 20, cursor: Optional[str] = None) -> CursorPage:
        """
        Cursor-based pagination providing steady O(1) seek performance on large datasets.
        """
        fetch_limit = limit + 1
        with self._connection() as conn:
            if cursor:
                try:
                    last_updated, last_id = self.decode_cursor(cursor)
                    query = """
                        SELECT project_id, title, scene_count, total_duration, created_at, updated_at
                        FROM projects
                        WHERE (updated_at < ?) OR (updated_at = ? AND project_id < ?)
                        ORDER BY updated_at DESC, project_id DESC
                        LIMIT ?
                    """
                    cursor_res = conn.execute(query, (last_updated, last_updated, last_id, fetch_limit))
                except Exception:
                    # Invalid cursor fallback to first page
                    query = """
                        SELECT project_id, title, scene_count, total_duration, created_at, updated_at
                        FROM projects
                        ORDER BY updated_at DESC, project_id DESC
                        LIMIT ?
                    """
                    cursor_res = conn.execute(query, (fetch_limit,))
            else:
                query = """
                    SELECT project_id, title, scene_count, total_duration, created_at, updated_at
                    FROM projects
                    ORDER BY updated_at DESC, project_id DESC
                    LIMIT ?
                """
                cursor_res = conn.execute(query, (fetch_limit,))

            rows = [dict(r) for r in cursor_res.fetchall()]

        has_more = len(rows) > limit
        if has_more:
            items = rows[:limit]
            last_item = items[-1]
            next_cursor = self.encode_cursor(last_item["updated_at"], last_item["project_id"])
        else:
            items = rows
            next_cursor = None

        return CursorPage(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
            limit=limit
        )

    def delete(self, project_id: str) -> bool:
        with self._connection() as conn:
            cursor = conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def export_to_file(plan: ProjectPlan, file_path: Path | str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def import_from_file(file_path: Path | str) -> Optional[ProjectPlan]:
        path = Path(file_path)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ProjectPlan.from_dict(data)
