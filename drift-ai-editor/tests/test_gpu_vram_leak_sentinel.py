import unittest
from pipeline.gpu_vram_leak_sentinel import GPUVRAMLeakSentinel


class TestGPUVRAMLeakSentinel(unittest.TestCase):
    def test_inspect_vram_clean_state(self):
        res = GPUVRAMLeakSentinel.inspect_vram_hygiene(estimated_allocated_vram_mb=800.0)
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["vram_leak_detected"])
        self.assertEqual(res["reclaimable_vram_mb"], 0.0)

    def test_inspect_vram_leak_detected(self):
        res = GPUVRAMLeakSentinel.inspect_vram_hygiene(estimated_allocated_vram_mb=2200.0)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["vram_leak_detected"])
        self.assertGreater(res["reclaimable_vram_mb"], 1000.0)


if __name__ == "__main__":
    unittest.main()
