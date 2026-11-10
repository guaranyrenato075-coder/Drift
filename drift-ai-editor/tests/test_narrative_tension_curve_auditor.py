import unittest
from models.scene_plan import ProjectPlan, Scene
from analysis.narrative_tension_curve_auditor import NarrativeTensionCurveAuditor


class TestNarrativeTensionCurveAuditor(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="A Jornada do Herói",
            scenes=[
                Scene(order=1, duration=5.0, narration_text="No início tudo era calmo e tranquilo na vila."),
                Scene(order=2, duration=6.0, narration_text="Mas um segredo obscuro trouxe uma terrível ameaça e conflito."),
                Scene(order=3, duration=7.0, narration_text="Era o momento de correr contra o tempo, a batalha final de destruição."),
                Scene(order=4, duration=4.0, narration_text="Finalmente a vitória foi alcançada com triunfo glorioso.")
            ]
        )

    def test_audit_narrative_tension(self):
        res = NarrativeTensionCurveAuditor.audit_narrative_tension(self.plan)
        self.assertEqual(res["total_scenes"], 4)
        self.assertGreater(res["peak_tension_score"], 60.0)
        self.assertEqual(len(res["tension_curve"]), 4)
        acts = [pt["act"] for pt in res["tension_curve"]]
        self.assertTrue(any("Ato 1" in a for a in acts))
        self.assertTrue(any("Ato 2" in a for a in acts))
        self.assertTrue(any("Ato 3" in a for a in acts))


if __name__ == "__main__":
    unittest.main()
