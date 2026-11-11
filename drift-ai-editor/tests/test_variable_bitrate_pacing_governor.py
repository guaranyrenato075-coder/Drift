import unittest
from media.variable_bitrate_pacing_governor import VariableBitratePacingGovernor


class TestVariableBitratePacingGovernor(unittest.TestCase):
    def test_vbv_calculation(self):
        res = VariableBitratePacingGovernor.calculate_vbv_parameters(
            target_bitrate_kbps=20000,
            encoder_family="nvenc",
            is_high_motion_scene=True
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["maxrate_kbps"], 20000)
        self.assertIn("-maxrate", res["ffmpeg_vbv_flags"])
        self.assertIn("-bufsize", res["ffmpeg_vbv_flags"])
        self.assertGreater(res["vrm_current_spike_suppression_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
