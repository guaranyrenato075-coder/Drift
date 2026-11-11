import unittest
from core.cpu_thread_affinity_governor import CPUThreadAffinityGovernor


class TestCPUThreadAffinityGovernor(unittest.TestCase):
    def test_get_system_logical_cores(self):
        cores = CPUThreadAffinityGovernor.get_system_logical_cores()
        self.assertGreaterEqual(cores, 1)

    def test_calculate_balanced_thread_allocation(self):
        res = CPUThreadAffinityGovernor.calculate_balanced_thread_allocation(
            reserved_cores_for_os=2,
            cooling_profile="balanced"
        )
        self.assertEqual(res["status"], "success")
        self.assertIn("hex_affinity_mask", res)
        self.assertIn("-threads", res["ffmpeg_thread_args"])
        self.assertGreaterEqual(res["allocated_render_threads"], 1)

    def test_silent_cool_profile(self):
        res = CPUThreadAffinityGovernor.calculate_balanced_thread_allocation(
            cooling_profile="silent_cool"
        )
        self.assertEqual(res["cooling_profile"], "silent_cool")


if __name__ == "__main__":
    unittest.main()
