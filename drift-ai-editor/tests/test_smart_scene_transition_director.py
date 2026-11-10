import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.smart_scene_transition_director import SmartSceneTransitionDirector


class TestSmartSceneTransitionDirector(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Transições Inteligentes",
            scenes=[
                Scene(order=1, narration_text="Esta foi a história de como tudo começou.", duration=8.0),
                Scene(order=2, narration_text="Mas de repente uma bomba explodiu no mercado.", duration=4.0),
                Scene(order=3, narration_text="Agora vamos analisar o próximo passo.", duration=3.0)
            ]
        )

    def test_get_transition_library(self):
        lib = SmartSceneTransitionDirector.get_transition_library()
        self.assertIn("glitch_flash", lib)
        self.assertIn("crossfade_dissolve", lib)
        self.assertIn("directional_wipe", lib)
        self.assertIn("zoom_blur_punch", lib)

    def test_plan_scene_transitions(self):
        res = SmartSceneTransitionDirector.plan_scene_transitions(self.plan)
        self.assertEqual(res["total_transitions"], 2)
        transitions = res["transitions"]
        # A transição entre 1 e 2 tem "Mas de repente uma bomba" -> glitch_flash
        self.assertEqual(transitions[0]["transition_type"], "glitch_flash")
        # A transição entre 2 e 3 tem "Agora vamos analisar o próximo passo" -> directional_wipe
        self.assertEqual(transitions[1]["transition_type"], "directional_wipe")


if __name__ == "__main__":
    unittest.main()
