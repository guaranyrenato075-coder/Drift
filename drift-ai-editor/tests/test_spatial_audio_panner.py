"""
Unit tests for BinauralSpatialAudioPanner in CutWire Drift AI.
Verifies binaural 3D panning trajectory selection and FFmpeg extrastereo/pan filter compilation.
"""
import unittest
from audio.spatial_audio_panner import BinauralSpatialAudioPanner
from models.scene_plan import ProjectPlan, Scene

class TestSpatialAudioPanner(unittest.TestCase):

    def test_calculate_pan_trajectory_movement(self):
        s1 = Scene(order=1, visual_description="Uma nave espacial cruza a tela em alta velocidade.")
        traj1 = BinauralSpatialAudioPanner.calculate_pan_trajectory(s1)
        self.assertEqual(traj1, "left_to_right")

        filt = BinauralSpatialAudioPanner.generate_pan_filter(traj1, 4.0)
        self.assertIn("extrastereo=", filt)
        self.assertIn("pan=stereo", filt)

    def test_calculate_pan_trajectory_ambient(self):
        s2 = Scene(order=2, visual_description="A imensidão silenciosa do universo e galáxias.")
        traj2 = BinauralSpatialAudioPanner.calculate_pan_trajectory(s2)
        self.assertEqual(traj2, "orbit_8d")

        filt = BinauralSpatialAudioPanner.generate_pan_filter(traj2, 5.0)
        self.assertIn("cos(", filt)
        self.assertIn("sin(", filt)

    def test_plan_spatial_audio_manifest(self):
        plan = ProjectPlan(title="Projeto Espacial 8D")
        plan.scenes = [
            Scene(order=1, visual_description="Meteoro voa rápido.", duration=3.0),
            Scene(order=2, visual_description="Espaço cósmico profundo.", duration=4.0)
        ]

        manifest = BinauralSpatialAudioPanner.plan_spatial_audio_manifest(plan)
        self.assertEqual(manifest["total_spatial_events"], 2)
        self.assertEqual(manifest["binaural_mode"], "Cinema 8D Spatial Immersive")

if __name__ == '__main__':
    unittest.main()
