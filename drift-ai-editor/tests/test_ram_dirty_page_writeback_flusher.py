import unittest
from core.ram_dirty_page_writeback_flusher import RAMDirtyPageWritebackFlusher


class TestRAMDirtyPageWritebackFlusher(unittest.TestCase):
    def test_idle_and_urgent_cadence(self):
        # Baixa quantidade de dirty pages
        idle_res = RAMDirtyPageWritebackFlusher.evaluate_writeback_cadence(estimated_dirty_mb=10.0)
        self.assertEqual(idle_res["status"], "success")
        self.assertEqual(idle_res["pacing_mode"], "IDLE_CLEAN")

        # Carga alta que atinge o limiar
        urgent_res = RAMDirtyPageWritebackFlusher.evaluate_writeback_cadence(estimated_dirty_mb=150.0)
        self.assertEqual(urgent_res["pacing_mode"], "URGENT_PACED")
        self.assertGreater(urgent_res["writeback_batch_mb"], 0.0)
        self.assertGreater(urgent_res["io_spike_reduction_pct"], 70.0)


if __name__ == "__main__":
    unittest.main()
