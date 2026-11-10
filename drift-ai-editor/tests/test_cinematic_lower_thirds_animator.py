import unittest
from models.scene_plan import ProjectPlan, Scene
from editing.cinematic_lower_thirds_animator import CinematicLowerThirdsAnimator


class TestCinematicLowerThirdsAnimator(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Vídeo com Lower Thirds",
            scenes=[
                Scene(order=1, concept="Especialista em IA", duration=6.0),
                Scene(order=2, concept="Cambridge, UK", duration=5.0)
            ]
        )

    def test_get_available_styles(self):
        styles = CinematicLowerThirdsAnimator.get_available_styles()
        self.assertIn("tech_cyber_bar", styles)
        self.assertIn("broadcast_news_slate", styles)
        self.assertIn("documentary_minimal", styles)
        self.assertIn("gold_luxury_serif", styles)

    def test_generate_lower_third_overlay(self):
        res = CinematicLowerThirdsAnimator.generate_lower_third_overlay(
            title="Dr. Alan Turing",
            subtitle="Pioneiro da Computação",
            style_name="tech_cyber_bar",
            start_time=2.0,
            duration=4.0
        )
        self.assertEqual(res["title"], "Dr. Alan Turing")
        self.assertIn("drawbox=", res["ffmpeg_filter"])
        self.assertIn("drawtext=", res["ffmpeg_filter"])
        self.assertIn("between(t,2.0,6.0)", res["ffmpeg_filter"])

    def test_generate_plan_lower_thirds(self):
        res = CinematicLowerThirdsAnimator.generate_plan_lower_thirds(self.plan, "documentary_minimal")
        self.assertEqual(res["total_lower_thirds"], 2)
        self.assertEqual(len(res["overlays"]), 2)


if __name__ == "__main__":
    unittest.main()
