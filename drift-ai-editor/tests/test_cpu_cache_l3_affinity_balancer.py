import unittest
from core.cpu_cache_l3_affinity_balancer import CPUCacheL3AffinityBalancer


class TestCPUCacheL3AffinityBalancer(unittest.TestCase):
    def test_calculate_affinity(self):
        res = CPUCacheL3AffinityBalancer.calculate_optimal_thread_affinity(total_threads=16)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["logical_cores_detected"], 16)
        self.assertEqual(len(res["primary_affinity_cores"]), 8)
        self.assertIn("0x", res["affinity_mask_hex"])
        self.assertGreater(res["bus_traffic_reduction_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
