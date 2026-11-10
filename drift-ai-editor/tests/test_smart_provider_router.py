"""
Unit tests for SmartProviderRouter and ConcurrentProviderSearch in Drift AI.
Verifies semantic cluster matching and threadpool parallel search capabilities.
"""
import unittest
from pipeline.smart_provider_router import SmartProviderRouter
from pipeline.concurrent_provider_search import ConcurrentProviderSearch
from models.scene_plan import Scene, SceneState

class TestSmartProviderRouter(unittest.TestCase):

    def test_classify_cluster_astronomy(self):
        cluster = SmartProviderRouter.classify_cluster("telescope deep space nebula galaxy star")
        self.assertEqual(cluster, "space_astronomy")

    def test_classify_cluster_food(self):
        cluster = SmartProviderRouter.classify_cluster("delicious pasta chef cuisine dish bakery")
        self.assertEqual(cluster, "food_culinary")

    def test_classify_cluster_philosophy_antiquity(self):
        cluster = SmartProviderRouter.classify_cluster("marcus aurelius marble bust sculpture rome")
        self.assertEqual(cluster, "history_antiquity_philosophy")

    def test_classify_cluster_nature(self):
        cluster = SmartProviderRouter.classify_cluster("yellowstone national park grizzly bear canyon")
        self.assertEqual(cluster, "nature_wildlife_geology")

    def test_route_providers_prioritization(self):
        # Para consulta astronômica, provedores como 'nasa', 'eso' devem vir antes de 'foodiesfeed'
        routed_names = SmartProviderRouter.route_providers(
            keywords=["mars", "space exploration", "nebula"]
        )
        self.assertIn("nasa", routed_names)
        self.assertIn("foodiesfeed", routed_names)
        self.assertLess(routed_names.index("nasa"), routed_names.index("foodiesfeed"))

    def test_route_providers_food_prioritization(self):
        # Para consulta culinária, 'foodiesfeed' deve vir antes de 'nasa'
        routed_names = SmartProviderRouter.route_providers(
            keywords=["gourmet", "pasta", "chef recipe"]
        )
        self.assertIn("foodiesfeed", routed_names)
        self.assertIn("nasa", routed_names)
        self.assertLess(routed_names.index("foodiesfeed"), routed_names.index("nasa"))

    def test_concurrent_provider_search_aggregates_candidates(self):
        scene = Scene(
            order=1,
            narration_text="The stars and cosmic galaxies shine across the universe.",
            visual_description="A high resolution view of space nebula and distant stars.",
            english_keywords=["space", "nebula", "galaxy"],
            duration=4.0
        )
        cands = ConcurrentProviderSearch.search_scene_candidates(
            scene=scene,
            plan_aspect_ratio="landscape",
            plan_media_type="image",
            target_candidates_count=3,
            max_providers_to_query=4
        )
        self.assertIsInstance(cands, list)
        self.assertGreaterEqual(len(cands), 1)
        self.assertTrue(all(hasattr(c, "platform") for c in cands))

if __name__ == "__main__":
    unittest.main()
