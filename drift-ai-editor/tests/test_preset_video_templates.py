"""
Unit tests for OneClickPresetVideoTemplates in CutWire Drift AI.
Verifies production profile listing and single-click application across plan configurations.
"""
import unittest
from pipeline.preset_video_templates import OneClickPresetVideoTemplates
from models.scene_plan import ProjectPlan, ProjectConfig

class TestPresetVideoTemplates(unittest.TestCase):

    def test_list_templates(self):
        templates = OneClickPresetVideoTemplates.list_templates()
        self.assertEqual(len(templates), 4)
        tmpl_ids = [t["id"] for t in templates]
        self.assertIn("space_scifi", tmpl_ids)
        self.assertIn("history_documentary", tmpl_ids)
        self.assertIn("viral_shorts", tmpl_ids)
        self.assertIn("business_tech", tmpl_ids)

    def test_apply_template_space_scifi(self):
        plan = ProjectPlan(title="Cosmos Explorer")
        plan.config = ProjectConfig(aspect_ratio="16:9")

        updated_plan = OneClickPresetVideoTemplates.apply_template_to_plan(plan, "space_scifi")

        self.assertEqual(updated_plan.config.aspect_ratio, "16:9")
        self.assertEqual(updated_plan.config.extra.get("template_id"), "space_scifi")
        self.assertEqual(updated_plan.config.extra.get("color_grading"), "deep_space")
        self.assertEqual(updated_plan.config.extra.get("subtitle_style"), "neon_glow")
        self.assertTrue(updated_plan.config.enable_ken_burns)

    def test_apply_template_viral_shorts(self):
        plan = ProjectPlan(title="Shorts Retenção")
        plan.config = ProjectConfig(aspect_ratio="16:9")

        updated_plan = OneClickPresetVideoTemplates.apply_template_to_plan(plan, "viral_shorts")

        self.assertEqual(updated_plan.config.aspect_ratio, "9:16")
        self.assertEqual(updated_plan.config.width, 1080)
        self.assertEqual(updated_plan.config.height, 1920)
        self.assertEqual(updated_plan.config.extra.get("template_id"), "viral_shorts")
        self.assertEqual(updated_plan.config.extra.get("subtitle_style"), "hormozi_viral")

if __name__ == '__main__':
    unittest.main()
