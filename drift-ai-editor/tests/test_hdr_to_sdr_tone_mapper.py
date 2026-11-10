import unittest
from models.scene_plan import ProjectPlan
from editing.hdr_to_sdr_tone_mapper import HDRToSDRToneMapper


class TestHDRToSDRToneMapper(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(title="Projeto HDR HLG")

    def test_get_available_presets(self):
        presets = HDRToSDRToneMapper.get_available_presets()
        self.assertIn("mobius_balanced", presets)
        self.assertIn("reinhard_soft_highlight", presets)
        self.assertIn("hable_cinematic", presets)
        self.assertIn("aces_filmic", presets)

    def test_build_tone_map_filter(self):
        f = HDRToSDRToneMapper.build_tone_map_filter("hable_cinematic")
        self.assertIn("zscale=", f)
        self.assertIn("tonemap=hable", f)
        self.assertIn("p=bt709", f)

    def test_apply_tone_mapping_to_plan(self):
        res = HDRToSDRToneMapper.apply_tone_mapping_to_plan(self.plan, "mobius_balanced")
        self.assertEqual(res["status"], "CONFIGURED")
        self.assertEqual(self.plan.hdr_tone_map_preset, "mobius_balanced")
        self.assertTrue(hasattr(self.plan, "hdr_tone_map_ffmpeg_filter"))


if __name__ == "__main__":
    unittest.main()
