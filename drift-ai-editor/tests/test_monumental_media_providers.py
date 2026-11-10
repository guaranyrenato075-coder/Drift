"""
Unit tests for monumental 70-provider milestone in CutWire Drift AI:
Artvee, Magdeleine, WordPress Photo Directory, Good Free Photos, and Jay Mantri.
Validates the milestone expansion to 70 global providers.
"""
import unittest
from providers.artvee import ArtveeProvider
from providers.magdeleine import MagdeleineProvider
from providers.wp_photos import WpPhotosProvider
from providers.goodfreephotos import GoodFreePhotosProvider
from providers.jay_mantri import JayMantriProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestMonumentalMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            ArtveeProvider(),
            MagdeleineProvider(),
            WpPhotosProvider(),
            GoodFreePhotosProvider(),
            JayMantriProvider()
        ]
        expected_names = {"artvee", "magdeleine", "wp_photos", "goodfreephotos", "jay_mantri"}
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_artvee_vintage_poster_search(self):
        p = ArtveeProvider()
        res = p.search("vintage travel railway poster 1930", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "artvee")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_magdeleine_moody_search(self):
        p = MagdeleineProvider()
        res = p.search("misty dark forest road cinematic", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "magdeleine")
        self.assertEqual(item.media_type, "image")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_wp_photos_open_community_search(self):
        p = WpPhotosProvider()
        res = p.search("workspace coding coffee modern", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "wp_photos")
        self.assertEqual(item.media_type, "image")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_goodfreephotos_landmark_search(self):
        p = GoodFreePhotosProvider()
        res = p.search("yellowstone canyon rocky mountain", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "goodfreephotos")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_jay_mantri_minimalist_search(self):
        p = JayMantriProvider()
        res = p.search("minimalist modern concrete architecture", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "jay_mantri")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lazy_registry_70_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertGreaterEqual(len(avail), 70, f"Expected at least 70 available providers in registry, found {len(avail)}")
        for name in [
            "artvee", "magdeleine", "wp_photos",
            "goodfreephotos", "jay_mantri"
        ]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
