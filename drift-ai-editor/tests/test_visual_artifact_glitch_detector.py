import unittest
from models.scene_plan import ProjectPlan, Scene
from analysis.visual_artifact_glitch_detector import VisualArtifactGlitchDetector


class TestVisualArtifactGlitchDetector(unittest.TestCase):
    def setUp(self):
        # Cria plano com uma cena sem mídia (risco black frame) e outra muito curta (< 1.2s)
        self.plan = ProjectPlan(
            title="Projeto Teste QC",
            scenes=[
                Scene(order=1, duration=5.0, narration_text="Introdução normal."),
                Scene(order=2, duration=0.8, narration_text="Cena ultra rápida sem mídia."),
                Scene(order=3, duration=15.0, narration_text="Cena muito longa e parada.")
            ]
        )

    def test_audit_project_visual_qc(self):
        qc = VisualArtifactGlitchDetector.audit_project_visual_qc(self.plan)
        self.assertEqual(qc["total_scenes_checked"], 3)
        self.assertGreater(qc["anomalies_found"], 0)
        types = [a["type"] for a in qc["anomalies"]]
        self.assertIn("BLACK_FRAME_RISK", types)
        self.assertIn("FLICKER_CUT_RISK", types)
        self.assertIn("STATIC_FREEZE_RISK", types)
        self.assertLess(qc["qc_score"], 100)


if __name__ == "__main__":
    unittest.main()
