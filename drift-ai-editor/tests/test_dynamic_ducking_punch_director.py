"""
Unit tests for DynamicZoomPunchAudioDuckingDirector in CutWire Drift AI.
Verifies sidechain ducking filter construction and vocal emphasis keyword punch-in detection.
"""
import unittest
from audio.dynamic_ducking_punch_director import DynamicZoomPunchAudioDuckingDirector
from models.scene_plan import ProjectPlan, Scene, ProjectConfig

class TestDynamicZoomPunchAudioDuckingDirector(unittest.TestCase):

    def test_calculate_sidechain_ducking_filter(self):
        filt = DynamicZoomPunchAudioDuckingDirector.calculate_sidechain_ducking_filter(
            duck_db=-14.0, attack_ms=25.0, release_ms=350.0, music_volume=0.20
        )
        self.assertIn("sidechaincompress=", filt)
        self.assertIn("threshold=0.10", filt)
        self.assertIn("attack=25.0", filt)
        self.assertIn("release=350.0", filt)
        self.assertIn("amix=inputs=2", filt)

    def test_detect_vocal_punch_in_triggers(self):
        plan = ProjectPlan(title="Projeto Mistério")
        plan.scenes = [
            Scene(order=1, narration_text="Esta é uma introdução normal.", duration=4.0),
            Scene(order=2, narration_text="Mas você nunca imaginaria a verdade secreta sobre o perigo iminente!", duration=5.0)
        ]

        triggers = DynamicZoomPunchAudioDuckingDirector.detect_vocal_punch_in_triggers(plan)
        self.assertGreaterEqual(len(triggers), 2)

        words = [t.trigger_word for t in triggers]
        self.assertIn("NUNCA", words)
        self.assertIn("VERDADE", words)
        self.assertIn("PERIGO", words)

        first = triggers[0]
        self.assertEqual(first.zoom_level, 1.12)
        self.assertEqual(first.duration_sec, 0.35)

    def test_generate_punchin_zoom_filter_and_plan(self):
        plan = ProjectPlan(title="Projeto Punch")
        plan.config = ProjectConfig(width=1920, height=1080)
        plan.scenes = [
            Scene(order=1, narration_text="O choque foi absurdo e inacreditável!", duration=4.0)
        ]

        manifest = DynamicZoomPunchAudioDuckingDirector.plan_ducking_and_punchins(plan)
        self.assertEqual(manifest["project_id"], plan.project_id)
        self.assertGreater(manifest["total_punch_triggers"], 0)
        self.assertIn("zoompan=z=", manifest["punch_in_filter"])
        self.assertIn("sidechaincompress=", manifest["sidechain_ducking_filter"])

if __name__ == '__main__':
    unittest.main()
