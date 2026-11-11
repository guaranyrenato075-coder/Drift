import unittest
from core.pcie_bandwidth_saturation_guard import PCIeBandwidthSaturationGuard


class TestPCIeBandwidthSaturationGuard(unittest.TestCase):
    def test_safe_pcie_transfer(self):
        res = PCIeBandwidthSaturationGuard.calculate_transfer_pacing(
            frame_width=1920,
            frame_height=1080,
            fps=60.0,
            pcie_generation="gen4"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["bus_safety_state"], "OPTIMAL")
        self.assertLess(res["bus_utilization_pct"], 50.0)

    def test_heavy_8k_transfer(self):
        res = PCIeBandwidthSaturationGuard.calculate_transfer_pacing(
            frame_width=7680,
            frame_height=4320,
            fps=60.0,
            pcie_generation="gen3"
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["bandwidth_required_gbps"], 5.0)


if __name__ == "__main__":
    unittest.main()
