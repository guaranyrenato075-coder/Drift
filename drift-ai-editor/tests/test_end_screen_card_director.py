"""
Unit tests for AIAutomatedEndScreenCardDirector in CutWire Drift AI.
Verifies outro card duration, YouTube Studio safe zone coordinates, and filter syntax.
"""
import unittest
from editing.end_screen_card_director import AIAutomatedEndScreenCardDirector
from models.scene_plan import ProjectPlan, ProjectConfig

class TestEndScreenCardDirector(unittest.TestCase):

    def test_generate_outro_template_1080p(self):
        plan = ProjectPlan(title="Fim do Documentário")
        plan.config = ProjectConfig(width=1920, height=1080)

        tmpl = AIAutomatedEndScreenCardDirector.generate_outro_template(plan, duration_sec=18.0)

        self.assertEqual(tmpl.duration_sec, 18.0)
        self.assertIn("x=", tmpl.video_recommendation_box)
        self.assertIn("size=160x160", tmpl.subscribe_avatar_pos)
        self.assertIn("drawbox=", tmpl.ffmpeg_outro_filter)
        self.assertIn("drawtext=", tmpl.ffmpeg_outro_filter)

    def test_plan_end_screen(self):
        plan = ProjectPlan(title="Mistério dos Oceanos")
        plan.config = ProjectConfig(width=1920, height=1080)

        res = AIAutomatedEndScreenCardDirector.plan_end_screen(plan)
        self.assertEqual(res["project_id"], plan.project_id)
        self.assertTrue(res["youtube_studio_ready"])
        self.assertEqual(res["end_screen_duration_sec"], 18.0)

if __name__ == '__main__':
    unittest.main()
