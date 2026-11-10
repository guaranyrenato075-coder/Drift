"""
Unit tests for AutoYouTubeCommunityPostPackager in CutWire Drift AI.
Verifies interactive poll formulation, teaser text generation, and discussion prompts.
"""
import unittest
from pipeline.youtube_community_packager import AutoYouTubeCommunityPostPackager
from models.scene_plan import ProjectPlan

class TestYouTubeCommunityPackager(unittest.TestCase):

    def test_generate_community_kit(self):
        plan = ProjectPlan(title="Mistérios de Marte e Vida Extraterrestre")
        kit = AutoYouTubeCommunityPostPackager.generate_community_kit(plan)

        self.assertEqual(kit.project_id, plan.project_id)
        # Check poll has 4 options
        self.assertEqual(len(kit.poll.options), 4)
        self.assertIn("Marte", kit.poll.poll_question)

        # Check teaser contains title and call to action
        self.assertIn("Marte", kit.teaser_post_text)
        self.assertIn("🔔", kit.teaser_post_text)

        # Check open discussion prompt
        self.assertIn("Marte", kit.open_discussion_question)
        self.assertIn("24h antes", kit.recommended_publish_timing)

    def test_export_kit_dict(self):
        plan = ProjectPlan(title="História Perdida de Roma")
        d = AutoYouTubeCommunityPostPackager.export_kit_dict(plan)

        self.assertEqual(d["project_id"], plan.project_id)
        self.assertIn("poll", d)
        self.assertIn("teaser_post_text", d)
        self.assertIn("open_discussion_question", d)

if __name__ == '__main__':
    unittest.main()
