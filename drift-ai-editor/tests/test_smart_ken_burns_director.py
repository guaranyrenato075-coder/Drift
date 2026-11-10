"""
Unit tests for SmartSceneKenBurnsDirector in CutWire Drift AI.
Verifies context-aware camera motions and mathematically valid FFmpeg zoompan expressions.
"""
import unittest
from editing.smart_ken_burns_director import SmartSceneKenBurnsDirector, CameraMotionConfig
from models.scene_plan import Scene, ProjectPlan, ProjectConfig

class TestSmartSceneKenBurnsDirector(unittest.TestCase):

    def test_portrait_face_zoom_in(self):
        scene = Scene(
            order=1,
            narration_text="O olhar penetrante do filósofo revelava sabedoria.",
            visual_description="Busto e rosto em close-up de um sábio clássico.",
            duration=4.0
        )
        motion = SmartSceneKenBurnsDirector.evaluate_scene_motion(scene, width=1920, height=1080, fps=30.0)

        self.assertEqual(motion.motion_type, "slow_zoom_in")
        self.assertIn("zoompan=", motion.ffmpeg_filter)
        self.assertIn("s=1920x1080", motion.ffmpeg_filter)
        self.assertIn("fps=30.0", motion.ffmpeg_filter)

    def test_climax_fast_push_in(self):
        scene = Scene(
            order=2,
            narration_text="Um choque absoluto quando ocorreu a explosão!",
            visual_description="Destruição dramática e fogo no horizonte.",
            duration=3.0
        )
        motion = SmartSceneKenBurnsDirector.evaluate_scene_motion(scene, width=1920, height=1080, fps=30.0)

        self.assertEqual(motion.motion_type, "fast_push_in")
        self.assertIn("1.35", motion.ffmpeg_filter)

    def test_wide_pan_or_pull_out(self):
        scene = Scene(
            order=2,  # Even order -> horizontal pan
            narration_text="A vastidão do cosmos com nebulosas distantes.",
            visual_description="Paisagem ampla da galáxia espiral no horizonte.",
            duration=5.0
        )
        motion = SmartSceneKenBurnsDirector.evaluate_scene_motion(scene, width=1920, height=1080, fps=30.0)

        self.assertEqual(motion.motion_type, "pan_horizontal")
        self.assertIn("zoompan=z='1.15'", motion.ffmpeg_filter)

    def test_generate_plan_camera_manifest(self):
        plan = ProjectPlan(title="Projeto de Câmera")
        plan.config = ProjectConfig(aspect_ratio="16:9", width=1920, height=1080, fps=30.0)
        plan.scenes = [
            Scene(order=1, narration_text="Introdução com rosto de personagem.", visual_description="Rosto clássico.", duration=4.0),
            Scene(order=2, narration_text="Uma explosão perigosa!", visual_description="Fogo e choque.", duration=3.0)
        ]

        manifest = SmartSceneKenBurnsDirector.generate_plan_camera_manifest(plan)
        self.assertEqual(manifest["project_id"], plan.project_id)
        self.assertEqual(manifest["total_scenes"], 2)
        self.assertEqual(len(manifest["camera_motions"]), 2)

if __name__ == '__main__':
    unittest.main()
