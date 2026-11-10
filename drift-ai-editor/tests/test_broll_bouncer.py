"""
Unit tests for BrollBouncer in Drift AI.
Verifies dynamic cutaway identification and retention boost calculation.
"""
import unittest
from editing.broll_bouncer import BrollBouncer, BrollCutaway
from models.scene_plan import ProjectPlan, Scene, MediaCandidate

class TestBrollBouncer(unittest.TestCase):

    def test_analyze_plan_cutaways(self):
        plan = ProjectPlan(title="B-Roll Test")
        c1 = MediaCandidate(candidate_id="c1", platform="nasa", download_url="http://test/1.jpg")
        c2 = MediaCandidate(candidate_id="c2", platform="eso", download_url="http://test/2.jpg")
        
        # Cena com 6.0s e 2 candidatos -> elegível para cutaway
        scene = Scene(order=1, narration_text="Long scene.", duration=6.0)
        scene.selected_media = c1
        scene.candidates = [c1, c2]
        plan.scenes = [scene]

        cutaways = BrollBouncer.analyze_plan_cutaways(plan, threshold_sec=4.5)
        self.assertEqual(len(cutaways), 1)
        self.assertEqual(cutaways[0].scene_order, 1)
        self.assertEqual(cutaways[0].main_media_platform, "nasa")
        self.assertEqual(cutaways[0].cutaway_media_platform, "eso")

    def test_apply_cutaways_to_plan(self):
        plan = ProjectPlan(title="B-Roll Test Apply")
        c1 = MediaCandidate(candidate_id="c1", platform="pexels", download_url="http://test/1.jpg")
        c2 = MediaCandidate(candidate_id="c2", platform="pixabay", download_url="http://test/2.jpg")
        scene = Scene(order=1, narration_text="Long scene.", duration=5.0)
        scene.selected_media = c1
        scene.candidates = [c1, c2]
        plan.scenes = [scene]

        result = BrollBouncer.apply_cutaways_to_plan(plan, threshold_sec=4.0)
        self.assertEqual(result["cutaways_injected"], 1)
        self.assertGreater(result["retention_boost_estimate_pct"], 0)
        self.assertIn("broll_cutaways", plan.config.extra)

if __name__ == "__main__":
    unittest.main()
