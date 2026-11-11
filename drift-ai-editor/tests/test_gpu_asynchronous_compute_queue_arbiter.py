import unittest
from pipeline.gpu_asynchronous_compute_queue_arbiter import GPUAsynchronousComputeQueueArbiter


class TestGPUAsynchronousComputeQueueArbiter(unittest.TestCase):
    def test_queue_distribution(self):
        res = GPUAsynchronousComputeQueueArbiter.dispatch_workload_plan(
            has_ai_upscaling=True,
            has_texture_upload=True,
            has_screen_render=True
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_queues_active"], 3)
        self.assertIn("Direct_3D_Queue", res["active_hardware_queues"])
        self.assertIn("Async_Compute_Queue", res["active_hardware_queues"])
        self.assertIn("Copy_Transfer_Queue", res["active_hardware_queues"])
        self.assertGreater(res["concurrency_efficiency_boost_pct"], 20.0)


if __name__ == "__main__":
    unittest.main()
