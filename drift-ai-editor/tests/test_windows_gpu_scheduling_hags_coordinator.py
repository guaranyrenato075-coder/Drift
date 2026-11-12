import unittest
from core.windows_gpu_scheduling_hags_coordinator import WindowsGPUSchedulingHAGSCoordinator


class TestWindowsGPUSchedulingHAGSCoordinator(unittest.TestCase):
    def test_detect_hags_status(self):
        res = WindowsGPUSchedulingHAGSCoordinator.detect_hags_status()
        self.assertEqual(res["status"], "success")
        self.assertIn("hags_active", res)
        self.assertIn("driver_model", res)
        self.assertIn("summary", res)

    def test_coordinate_command_batching(self):
        batch = WindowsGPUSchedulingHAGSCoordinator.coordinate_command_batching(target_fps=60)
        self.assertEqual(batch["status"], "success")
        self.assertEqual(batch["target_fps"], 60)
        self.assertGreater(batch["cpu_hardware_interrupts_prevented_per_sec"], 0)


if __name__ == "__main__":
    unittest.main()
