"""
Unit tests for AIAutomatedThumbnailVariatorAB in CutWire Drift AI.
Verifies YouTube A/B/C/D thumbnail variant generation and overlay filter parameters.
"""
import unittest
from pipeline.thumbnail_variator_ab import AIAutomatedThumbnailVariatorAB
from models.scene_plan import ProjectPlan

class TestThumbnailVariatorAB(unittest.TestCase):

    def test_generate_thumbnail_quad(self):
        plan = ProjectPlan(title="O Enigma das Pirâmides")
        variants = AIAutomatedThumbnailVariatorAB.generate_thumbnail_quad(plan)

        self.assertEqual(len(variants), 4)
        var_ids = [v.variant_id for v in variants]
        self.assertIn("variant_a", var_ids)
        self.assertIn("variant_b", var_ids)
        self.assertIn("variant_c", var_ids)
        self.assertIn("variant_d", var_ids)

        # Variant A has high contrast vignette
        self.assertIn("vignette", variants[0].overlay_filter)
        # Variant B has bold text box
        self.assertIn("drawbox", variants[1].overlay_filter)
        # Variant D has split grid
        self.assertIn("drawgrid", variants[3].overlay_filter)

    def test_plan_thumbnail_suite(self):
        plan = ProjectPlan(title="Mistérios do Oceano Profundo")
        res = AIAutomatedThumbnailVariatorAB.plan_thumbnail_suite(plan)

        self.assertEqual(res["project_id"], plan.project_id)
        self.assertEqual(res["total_variants"], 4)
        self.assertTrue(res["youtube_test_and_compare_ready"])

if __name__ == '__main__':
    unittest.main()
