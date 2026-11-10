"""
Unit tests for DiskSpaceGuard in Drift AI.
Verifies system storage health checks and hygiene routines.
"""
import unittest
from storage.disk_space_guard import DiskSpaceGuard, DiskHealth

class TestDiskSpaceGuard(unittest.TestCase):

    def test_check_health(self):
        health = DiskSpaceGuard.check_health("C:\\")
        self.assertIsInstance(health, DiskHealth)
        self.assertIsInstance(health.free_gb, float)
        self.assertIsInstance(health.total_gb, float)
        self.assertGreater(health.total_gb, 0.0)
        self.assertIsInstance(health.is_healthy, bool)
        self.assertIsInstance(health.warnings, list)

    def test_disk_health_dict_serialization(self):
        health = DiskSpaceGuard.check_health("C:\\")
        data = health.__dict__
        self.assertIn("drive", data)
        self.assertIn("free_gb", data)
        self.assertIn("total_gb", data)
        self.assertIn("is_healthy", data)

    def test_ensure_healthy_space_safe_execution(self):
        # Valida que ensure_healthy_space executa sem erros e retorna os bytes liberados (int)
        freed = DiskSpaceGuard.ensure_healthy_space(min_free_gb=0.1)
        self.assertIsInstance(freed, int)
        self.assertGreaterEqual(freed, 0)

if __name__ == "__main__":
    unittest.main()
