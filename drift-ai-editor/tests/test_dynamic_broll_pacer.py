import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.dynamic_broll_pacer import DynamicBrollPacer


class TestDynamicBrollPacer(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="A Origem da IA",
            scenes=[
                Scene(order=1, narration_text="Introdução rápida e direta.", duration=3.0),
                Scene(order=2, narration_text="Esta é uma cena muito longa que fala sobre computadores gigantes e a revolução digital da década de cinquenta.", duration=8.0),
                Scene(order=3, narration_text="Conclusão objetiva.", duration=2.5)
            ]
        )

    def test_calculate_broll_pacing_detects_static_risk(self):
        analysis = DynamicBrollPacer.calculate_broll_pacing(self.plan, max_static_duration=4.5)
        self.assertEqual(analysis["total_scenes"], 3)
        self.assertEqual(analysis["static_risk_count"], 1)
        self.assertEqual(len(analysis["recommendations"]), 1)
        rec = analysis["recommendations"][0]
        self.assertEqual(rec["scene_index"], 2)
        self.assertGreater(rec["duration"], 0)

    def test_auto_insert_broll_slots(self):
        res = DynamicBrollPacer.auto_insert_broll_slots(self.plan, max_static_duration=4.5)
        self.assertEqual(res["slots_created"], 1)
        self.assertTrue(hasattr(self.plan.scenes[1], "broll_inserts"))
        self.assertEqual(len(self.plan.scenes[1].broll_inserts), 1)


if __name__ == "__main__":
    unittest.main()
