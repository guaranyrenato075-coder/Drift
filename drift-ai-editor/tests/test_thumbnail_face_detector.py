import unittest
from models.scene_plan import ProjectPlan, Scene
from analysis.thumbnail_face_detector import AIAutomatedThumbnailFaceDetector


class TestThumbnailFaceDetector(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Vídeo com Expressões Fortes",
            scenes=[
                Scene(order=1, duration=5.0, narration_text="Uma descoberta chocante e perigosa que destruiu tudo."),
                Scene(order=2, duration=4.0, narration_text="Uma vitória com lucro de milhões incrível."),
                Scene(order=3, duration=3.0, narration_text="Texto comum sem expressão.")
            ]
        )

    def test_detect_thumbnail_face_candidates(self):
        res = AIAutomatedThumbnailFaceDetector.detect_thumbnail_face_candidates(self.plan)
        self.assertEqual(res["status"], "DETECTED")
        cands = res["top_thumbnail_candidates"]
        self.assertGreater(len(cands), 0)
        first = cands[0]
        self.assertIn("face_bounding_box", first)
        self.assertIn("rule_of_thirds_anchor", first)
        self.assertIn("suggested_crop_filter", first)
        self.assertGreaterEqual(first["ctr_expressiveness_score"], 80.0)


if __name__ == "__main__":
    unittest.main()
