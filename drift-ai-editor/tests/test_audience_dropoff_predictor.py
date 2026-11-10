import unittest
from models.scene_plan import ProjectPlan, Scene
from analysis.audience_dropoff_predictor import AudienceDropoffPredictor


class TestAudienceDropoffPredictor(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Vídeo com Queda de Audiência",
            scenes=[
                Scene(order=1, duration=30.0, narration_text="Uma introdução muito longa e sem gancho."),
                Scene(order=2, duration=8.0, narration_text="Uma cena monótona sem palavras de ação.")
            ]
        )

    def test_predict_dropoff_hotspots(self):
        res = AudienceDropoffPredictor.predict_dropoff_hotspots(self.plan)
        self.assertEqual(res["total_scenes"], 2)
        self.assertGreater(res["dropoff_risks_count"], 0)
        self.assertIn("%", res["predicted_average_retention"])
        first_hotspot = res["dropoff_hotspots"][0]
        self.assertIn("timestamp", first_hotspot)
        self.assertIn("remedy", first_hotspot)


if __name__ == "__main__":
    unittest.main()
