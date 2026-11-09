"""
Unit tests for specialized domain media providers in CutWire Drift AI:
National Park Service (NPS), Foodiesfeed, The Walters Art Museum,
CDC Public Health Image Library (PHIL), Old Book Illustrations, and Morguefile.
Validates the milestone expansion to 58 global providers.
"""
import unittest
from providers.nps import NpsProvider
from providers.foodiesfeed import FoodiesfeedProvider
from providers.walters_art import WaltersArtProvider
from providers.cdc_phil import CdcPhilProvider
from providers.old_book_illustrations import OldBookIllustrationsProvider
from providers.morguefile import MorguefileProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestSpecializedMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            NpsProvider(),
            FoodiesfeedProvider(),
            WaltersArtProvider(),
            CdcPhilProvider(),
            OldBookIllustrationsProvider(),
            MorguefileProvider()
        ]
        expected_names = {
            "nps", "foodiesfeed", "walters_art",
            "cdc_phil", "old_book_illustrations", "morguefile"
        }
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_nps_nature_wildlife_search(self):
        p = NpsProvider()
        res = p.search("yellowstone canyon waterfall", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "nps")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_foodiesfeed_culinary_search(self):
        p = FoodiesfeedProvider()
        res = p.search("espresso gourmet bakery dessert", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "foodiesfeed")
        self.assertEqual(item.media_type, "image")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_walters_antiquity_search(self):
        p = WaltersArtProvider()
        res = p.search("medieval illuminated knight armor", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "walters_art")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_cdc_phil_medical_search(self):
        p = CdcPhilProvider()
        res = p.search("microscopic virus neuron laboratory", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "cdc_phil")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_old_book_vintage_engraving_search(self):
        p = OldBookIllustrationsProvider()
        res = p.search("victorian gothic mythology drawing", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "old_book_illustrations")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_morguefile_real_life_search(self):
        p = MorguefileProvider()
        res = p.search("city street morning texture", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "morguefile")
        self.assertEqual(item.media_type, "image")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lazy_registry_58_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertGreaterEqual(len(avail), 58, f"Expected at least 58 available providers in registry, found {len(avail)}")
        for name in [
            "nps", "foodiesfeed", "walters_art",
            "cdc_phil", "old_book_illustrations", "morguefile"
        ]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
