import unittest
from storage.ssd_write_fatigue_mitigator import SSDWriteFatigueMitigator


class TestSSDWriteFatigueMitigator(unittest.TestCase):
    def test_calculate_write_savings(self):
        # 500 MB de dados intermediários
        res = SSDWriteFatigueMitigator.calculate_write_savings(500 * 1024 * 1024, use_ram_scratchpad=True)
        self.assertEqual(res["status"], "success")
        self.assertAlmostEqual(res["raw_temp_data_mb"], 500.0)
        self.assertGreater(res["saved_ssd_writes_mb"], 0.0)
        self.assertGreaterEqual(res["ssd_life_extension_pct"], 80.0)

    def test_get_optimal_scratchpad_strategy(self):
        res16 = SSDWriteFatigueMitigator.get_optimal_scratchpad_strategy(16.0)
        self.assertEqual(res16["allocated_scratchpad_mb"], 2048)

        res32 = SSDWriteFatigueMitigator.get_optimal_scratchpad_strategy(32.0)
        self.assertEqual(res32["allocated_scratchpad_mb"], 4096)


if __name__ == "__main__":
    unittest.main()
