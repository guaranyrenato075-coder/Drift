import unittest
from pipeline.gpu_compute_memory_barrier_guard import GPUComputeMemoryBarrierGuard


class TestGPUComputeMemoryBarrierGuard(unittest.TestCase):
    def test_generate_barrier_sync_policy(self):
        res = GPUComputeMemoryBarrierGuard.generate_barrier_sync_policy(
            hw_acceleration="d3d11va",
            fps=30.0,
            enable_double_buffering=True
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["vram_ring_buffer_frames"], 4)
        self.assertIn("-extra_hw_frames 4", res["ffmpeg_sync_args"])
        self.assertGreater(res["gpu_stall_reduction_pct"], 80.0)


if __name__ == "__main__":
    unittest.main()
