"""
Unit tests for SmartSceneTransitionDirector in Drift AI.
Verifies dramatic transition evaluation, temporal dips, shock cuts, and full timeline planning.
"""
import unittest
from editing.smart_transition_director import SmartSceneTransitionDirector, SceneTransitionPlan
from models.scene_plan import ProjectPlan, Scene

class TestSmartTransitionDirector(unittest.TestCase):

    def test_evaluate_shock_hard_cut(self):
        s1 = Scene(order=1, narration_text="Tudo parecia pacífico na cidade antiga.")
        s2 = Scene(order=2, narration_text="De repente, um perigo inesperado e uma tragédia chocaram todos.")
        t = SmartSceneTransitionDirector.evaluate_transition(s1, s2)
        self.assertIsInstance(t, SceneTransitionPlan)
        self.assertEqual(t.transition_type, "hard_cut")
        self.assertEqual(t.duration_sec, 0.0)

    def test_evaluate_temporal_dip_to_black(self):
        s1 = Scene(order=1, narration_text="O império viveu sua era de ouro.")
        s2 = Scene(order=2, narration_text="Séculos depois, novas eras transformaram a região.")
        t = SmartSceneTransitionDirector.evaluate_transition(s1, s2)
        self.assertEqual(t.transition_type, "dip_to_black")
        self.assertGreater(t.duration_sec, 0.5)

    def test_plan_project_transitions(self):
        plan = ProjectPlan(title="Projeto Transições")
        plan.scenes = [
            Scene(order=1, narration_text="Início normal."),
            Scene(order=2, narration_text="Continuação suave da mesma ideia."),
            Scene(order=3, narration_text="Uma tragédia chocante destruiu a fortaleza.")
        ]
        transitions = SmartSceneTransitionDirector.plan_project_transitions(plan)
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0].transition_type, "crossfade")
        self.assertEqual(transitions[1].transition_type, "hard_cut")

if __name__ == "__main__":
    unittest.main()
