import unittest
import sqlite3
import tempfile
import os
from pathlib import Path
from storage.sqlite_wal_checkpoint_governor import SQLiteWALCheckpointGovernor


class TestSQLiteWALCheckpointGovernor(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        # Inicializa banco em modo WAL
        conn = sqlite3.connect(self.temp_db.name)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("CREATE TABLE test (id INT, val TEXT);")
        conn.execute("INSERT INTO test VALUES (1, 'demo');")
        conn.commit()
        conn.close()

    def tearDown(self):
        for ext in ("", "-wal", "-shm"):
            p = f"{self.temp_db.name}{ext}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def test_execute_passive_checkpoint(self):
        res = SQLiteWALCheckpointGovernor.execute_passive_checkpoint(Path(self.temp_db.name))
        self.assertEqual(res["status"], "success")
        self.assertIn("pages_checkpointed", res)


if __name__ == "__main__":
    unittest.main()
