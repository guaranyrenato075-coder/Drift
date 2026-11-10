"""
Unit tests for AIStoryHookABSplitTester in CutWire Drift AI.
Verifies psychological hook archetype generation and application to plan intro.
"""
import unittest
from pipeline.story_hook_split_tester import AIStoryHookABSplitTester
from models.scene_plan import ProjectPlan, Scene

class TestStoryHookSplitTester(unittest.TestCase):

    def test_generate_hook_variations(self):
        plan = ProjectPlan(title="Mistérios de Atlântida")
        variations = AIStoryHookABSplitTester.generate_hook_variations(plan)

        self.assertEqual(len(variations), 3)
        archetypes = [v.archetype for v in variations]
        self.assertIn("provocative_question", archetypes)
        self.assertIn("climactic_revelation", archetypes)
        self.assertIn("counter_intuitive", archetypes)

        for v in variations:
            self.assertGreaterEqual(v.estimated_hook_power, 90)
            self.assertIn("Atlântida", v.narration_text)

    def test_apply_hook_to_plan(self):
        plan = ProjectPlan(title="Segredos do Tempo")
        plan.scenes = [
            Scene(order=1, narration_text="Texto antigo", duration=8.0)
        ]

        updated = AIStoryHookABSplitTester.apply_hook_to_plan(plan, "hook_climactic_revelation")
        self.assertIn("Em poucos segundos", updated.scenes[0].narration_text)
        self.assertLessEqual(updated.scenes[0].duration, 5.0)
        self.assertEqual(updated.config.extra["active_story_hook"]["hook_id"], "hook_climactic_revelation")

if __name__ == '__main__':
    unittest.main()
