import unittest
from models.scene_plan import ProjectPlan, Scene
from analysis.visual_symmetry_aesthetic_auditor import VisualSymmetryAestheticAuditor


class TestVisualSymmetryAestheticAuditor(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Estética Kubrick",
            scenes=[
                Scene(order=1, concept="Corredor central simétrico", visual_description="Plano frontal do sujeito olhando para a câmera com horizonte profundo."),
                Scene(order=2, concept="Movimento rápido", visual_description="Câmera correndo pela floresta.")
            ]
        )

    def test_audit_composition_symmetry(self):
        res = VisualSymmetryAestheticAuditor.audit_composition_symmetry(self.plan)
        self.assertEqual(res["total_scenes_audited"], 2)
        self.assertGreater(res["average_aesthetic_score"], 60.0)
        self.assertEqual(len(res["evaluations"]), 2)
        # Primeira cena deve ter pontuação superior devido ao enquadramento centralizado
        self.assertGreater(res["evaluations"][0]["composition_score"], res["evaluations"][1]["composition_score"])


if __name__ == "__main__":
    unittest.main()
