"""
Unit tests for SmartAudienceRetentionPacer in CutWire Drift AI.
Verifies Hollywood dopamine wave pacing calculation and scene duration optimization.
"""
import unittest
from editing.retention_pacer import SmartAudienceRetentionPacer
from models.scene_plan import ProjectPlan, Scene

class TestRetentionPacer(unittest.TestCase):

    def test_calculate_pacing_waves(self):
        plan = ProjectPlan(title="Projeto de Pacing")
        plan.scenes = [
            Scene(order=1, narration_text="Introdução misteriosa.", duration=5.0),
            Scene(order=2, narration_text="Desenvolvimento inicial.", duration=4.0),
            Scene(order=3, narration_text="Um perigo e choque terrível!", duration=4.5),
            Scene(order=4, narration_text="Conclusão e encerramento.", duration=3.0)
        ]

        res = SmartAudienceRetentionPacer.calculate_pacing_waves(plan)

        self.assertEqual(res["total_scenes_paced"], 4)
        beats = res["pacing_beats"]

        # Scene 1 is tension build (capped at 3.2s)
        self.assertLessEqual(beats[0]["optimized_duration"], 3.2)
        # Scene 3 is high intensity keywords -> information burst
        self.assertEqual(beats[2]["rhythm_phase"], "information_burst")
        self.assertLessEqual(beats[2]["optimized_duration"], 2.2)
        # Scene 4 is resolution
        self.assertEqual(beats[3]["rhythm_phase"], "resolution")

if __name__ == '__main__':
    unittest.main()
