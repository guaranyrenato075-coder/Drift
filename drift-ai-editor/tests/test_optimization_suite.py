"""
Unit and integration tests for Surgical Optimization Suite:
LazyProviderRegistry, MemoryManager, SmartCache, ContextPruner,
ProjectRepository (Cursor-Based Pagination & Surgical Indexes).
"""
import time
import tempfile
import unittest
from pathlib import Path

from models.scene_plan import ProjectPlan, Scene
from core.lazy_provider_registry import LazyProviderRegistry
from core.memory_manager import MemoryManager
from core.smart_cache import SmartCache, cached
from director.context_pruner import ContextPruner
from storage.repository import ProjectRepository

class TestOptimizationSuite(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.tmp_dir) / "test_cursor.db"
        self.repo = ProjectRepository(self.db_path)

    def test_lazy_provider_registry(self):
        LazyProviderRegistry.unload_idle()
        self.assertEqual(len(LazyProviderRegistry.get_all_active()), 0)

        # On-demand loading
        p_pexels = LazyProviderRegistry.get_provider("pexels")
        self.assertIsNotNone(p_pexels)
        self.assertEqual(p_pexels.name, "pexels")
        self.assertEqual(len(LazyProviderRegistry.get_all_active()), 1)

        # Cache reuse
        p_pexels_again = LazyProviderRegistry.get_provider("pexels")
        self.assertIs(p_pexels, p_pexels_again)

        # Unload
        LazyProviderRegistry.unload_idle()
        self.assertEqual(len(LazyProviderRegistry.get_all_active()), 0)

    def test_memory_manager(self):
        rss = MemoryManager.get_memory_usage_mb()
        self.assertGreaterEqual(rss, 0.0)

        stats = MemoryManager.get_stats()
        self.assertIsNotNone(stats.python_version)
        self.assertGreaterEqual(stats.rss_mb, 0.0)

        res = MemoryManager.collect_garbage(trim_os_working_set=True)
        self.assertIn("collected_objects", res)
        self.assertIn("mem_before_mb", res)
        self.assertIn("mem_after_mb", res)

        # Context manager guard
        with MemoryManager.memory_guard("test_job"):
            dummy_alloc = [b"x" * 1024 for _ in range(100)]
            self.assertEqual(len(dummy_alloc), 100)

    def test_smart_cache(self):
        cache = SmartCache(max_entries=3, default_ttl_sec=1)
        cache.set("k1", {"val": "alpha"}, ttl_sec=1)
        cache.set("k2", {"val": "beta"}, ttl_sec=1)

        self.assertEqual(cache.get("k1"), {"val": "alpha"})
        self.assertEqual(cache.get("k2"), {"val": "beta"})
        self.assertIsNone(cache.get("nonexistent"))

        # Test LRU eviction (insert k3, k4 -> k1 was accessed, so k2 gets evicted if LRU is enforced)
        cache.set("k3", {"val": "gamma"}, ttl_sec=5)
        cache.get("k1") # refresh k1
        cache.set("k4", {"val": "delta"}, ttl_sec=5)
        # Capacity is 3 -> k2 should be evicted
        self.assertIsNone(cache.get("k2"))
        self.assertIsNotNone(cache.get("k1"))
        self.assertIsNotNone(cache.get("k4"))

        # Test TTL expiration
        cache_fast = SmartCache(default_ttl_sec=0) # Expires immediately
        cache_fast.set("temp", "value", ttl_sec=0)
        time.sleep(0.01)
        self.assertIsNone(cache_fast.get("temp"))

    def test_context_pruner(self):
        # 1. Tool bloat stripping
        huge_blob = "{" + ("'cand': 123, " * 100) + "}"
        pruned_blob = ContextPruner.strip_tool_bloat(huge_blob, max_chars=80)
        self.assertLess(len(pruned_blob), len(huge_blob))
        self.assertIn("[Truncated", pruned_blob)

        # 2. Sliding window history pruning
        history = [
            {"role": "user", "content": "Primeira mensagem sobre edição"},
            {"role": "assistant", "content": "Entendido, vamos editar"},
            {"role": "user", "content": "Segunda mensagem sobre corte"},
            {"role": "assistant", "content": "Corte agendado"},
            {"role": "user", "content": "Terceira mensagem sobre trilha sonora"},
            {"role": "assistant", "content": "Trilha sonora ajustada"},
            {"role": "user", "content": "Quarta mensagem: acelere a cena 1"},
        ]

        pruned = ContextPruner.prune_history(
            history,
            max_turns=3,
            max_token_budget=1000,
            system_prompt="Você é o assistente CutWire Drift."
        )

        self.assertEqual(pruned.messages[0]["role"], "system")
        self.assertEqual(pruned.messages[0]["content"], "Você é o assistente CutWire Drift.")
        # Preserved 3 turns + system prompt + memory capsule
        self.assertGreater(pruned.pruned_turns_count, 0)
        self.assertIsNotNone(pruned.memory_capsule)
        self.assertIn("Memória de Contexto Anterior", pruned.memory_capsule)

    def test_cursor_based_pagination(self):
        # Insert 5 test projects with distinct timestamps
        for i in range(5):
            p = ProjectPlan(title=f"Projeto {i+1}")
            p.scenes = [Scene(order=1, narration_text="Texto", duration=3.0)]
            self.repo.save(p)
            time.sleep(0.02) # Ensure descending timestamp differences

        # Check total count via list_all
        all_items = self.repo.list_all()
        self.assertEqual(len(all_items), 5)

        # Page 1: limit 2
        page1 = self.repo.list_cursor(limit=2)
        self.assertEqual(len(page1.items), 2)
        self.assertTrue(page1.has_more)
        self.assertIsNotNone(page1.next_cursor)
        self.assertEqual(page1.items[0]["title"], "Projeto 5") # Most recently updated

        # Page 2: limit 2 from cursor
        page2 = self.repo.list_cursor(limit=2, cursor=page1.next_cursor)
        self.assertEqual(len(page2.items), 2)
        self.assertTrue(page2.has_more)
        self.assertIsNotNone(page2.next_cursor)
        self.assertNotEqual(page1.items[0]["project_id"], page2.items[0]["project_id"])

        # Page 3: limit 2 from cursor (final page with 1 remaining item)
        page3 = self.repo.list_cursor(limit=2, cursor=page2.next_cursor)
        self.assertEqual(len(page3.items), 1)
        self.assertFalse(page3.has_more)
        self.assertIsNone(page3.next_cursor)

        # Verify no items were skipped or duplicated
        retrieved_ids = [it["project_id"] for it in page1.items + page2.items + page3.items]
        expected_ids = [it["project_id"] for it in all_items]
        self.assertEqual(retrieved_ids, expected_ids)

    def test_sqlite_surgical_indexes(self):
        with self.repo._connection() as conn:
            cursor = conn.execute("PRAGMA index_list('projects')")
            indexes = [r["name"] for r in cursor.fetchall()]
            self.assertIn("idx_projects_cursor", indexes)
            self.assertIn("idx_projects_created", indexes)
            self.assertIn("idx_projects_title", indexes)

            # Check WAL journal mode
            mode_cur = conn.execute("PRAGMA journal_mode")
            mode = mode_cur.fetchone()[0]
            self.assertEqual(mode.lower(), "wal")

if __name__ == "__main__":
    unittest.main()

