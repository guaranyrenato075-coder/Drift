import unittest
from models.scene_plan import ProjectPlan
from audio.stereo_to_51_surround_upmixer import StereoTo51SurroundUpmixer


class TestStereoTo51SurroundUpmixer(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(title="Projeto Surround 5.1")

    def test_build_51_surround_filter(self):
        res = StereoTo51SurroundUpmixer.build_51_surround_filter(center_dialogue_boost_db=2.5)
        self.assertEqual(res["channels_count"], 6)
        self.assertEqual(res["channel_layout"], "5.1(side)")
        self.assertIn("pan=5.1", res["ffmpeg_audio_filter"])
        self.assertIn("c2=0.5*c0+0.5*c1", res["ffmpeg_audio_filter"]) # Canal central

    def test_apply_51_upmix_to_plan(self):
        res = StereoTo51SurroundUpmixer.apply_51_upmix_to_plan(self.plan, center_dialogue_boost_db=3.0)
        self.assertEqual(res["status"], "APPLIED")
        self.assertTrue(hasattr(self.plan, "surround_51_config"))


if __name__ == "__main__":
    unittest.main()
