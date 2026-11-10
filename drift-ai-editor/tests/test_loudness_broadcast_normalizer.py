"""
Unit tests for SmartLoudnessBroadcastNormalizer in CutWire Drift AI.
Verifies EBU R128 and YouTube -14 LUFS loudness specifications and command syntax.
"""
import unittest
from audio.loudness_broadcast_normalizer import SmartLoudnessBroadcastNormalizer
from models.scene_plan import ProjectPlan

class TestLoudnessBroadcastNormalizer(unittest.TestCase):

    def test_get_filter_for_platform_youtube(self):
        spec = SmartLoudnessBroadcastNormalizer.get_filter_for_platform("youtube")
        self.assertEqual(spec.target_integrated_lufs, -14.0)
        self.assertEqual(spec.true_peak_dbtp, -1.0)
        self.assertEqual(spec.loudness_range_lra, 7.0)
        self.assertIn("loudnorm=I=-14", spec.ffmpeg_loudnorm_filter)

    def test_build_loudnorm_command(self):
        cmd = SmartLoudnessBroadcastNormalizer.build_loudnorm_command("input.wav", "output.wav", "youtube")
        self.assertIn("ffmpeg -y -i input.wav", cmd)
        self.assertIn("-af \"loudnorm=I=-14:LRA=7:tp=-1.0\"", cmd)
        self.assertIn("output.wav", cmd)

    def test_audit_and_plan_normalization(self):
        plan = ProjectPlan(title="Projeto Áudio Cristalino")
        res = SmartLoudnessBroadcastNormalizer.audit_and_plan_normalization(plan)

        self.assertEqual(res["target_lufs"], -14.0)
        self.assertTrue(res["algorithm_penalty_protected"])
        self.assertGreaterEqual(len(res["all_presets"]), 3)

if __name__ == '__main__':
    unittest.main()
