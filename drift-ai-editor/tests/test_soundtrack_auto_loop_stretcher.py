import unittest
from models.scene_plan import ProjectPlan, Scene
from audio.soundtrack_auto_loop_stretcher import SoundtrackAutoLoopStretcher


class TestSoundtrackAutoLoopStretcher(unittest.TestCase):
    def test_calculate_soundtrack_stretch_direct_fit(self):
        # Vídeo de 60s com música de 120s -> não precisa de loop
        res = SoundtrackAutoLoopStretcher.calculate_soundtrack_stretch(
            video_duration_seconds=60.0,
            soundtrack_duration_seconds=120.0
        )
        self.assertFalse(res["needs_loop"])
        self.assertEqual(res["loops_required"], 1)
        self.assertIn("afade=t=out", res["ffmpeg_filter"])

    def test_calculate_soundtrack_stretch_needs_loop(self):
        # Vídeo de 300s (5min) com música de 100s -> precisa de múltiplos loops
        res = SoundtrackAutoLoopStretcher.calculate_soundtrack_stretch(
            video_duration_seconds=300.0,
            soundtrack_duration_seconds=100.0,
            crossfade_seconds=3.0
        )
        self.assertTrue(res["needs_loop"])
        self.assertGreater(res["loops_required"], 1)
        self.assertIn("aloop=", res["ffmpeg_filter"])

    def test_stretch_plan_soundtrack(self):
        plan = ProjectPlan(
            title="Projeto Longo",
            scenes=[Scene(order=1, duration=150.0)]
        )
        res = SoundtrackAutoLoopStretcher.stretch_plan_soundtrack(plan, soundtrack_duration_seconds=60.0)
        self.assertTrue(res["needs_loop"])
        self.assertTrue(hasattr(plan, "soundtrack_loop_config"))


if __name__ == "__main__":
    unittest.main()
