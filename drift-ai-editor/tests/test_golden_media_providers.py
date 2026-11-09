"""
Unit tests for golden milestone media providers in CutWire Drift AI:
Reshot, Life of Pix & Life of Vids, and Flickr Commons.
Validates the milestone expansion to 52 global providers.
"""
import unittest
from providers.reshot import ReshotProvider
from providers.lifeofpix import LifeOfPixProvider
from providers.flickr_commons import FlickrCommonsProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestGoldenMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            ReshotProvider(),
            LifeOfPixProvider(),
            FlickrCommonsProvider()
        ]
        expected_names = {"reshot", "lifeofpix", "flickr_commons"}
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_reshot_authentic_search(self):
        p = ReshotProvider()
        res = p.search("creative portrait photography", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "reshot")
        self.assertEqual(item.media_type, "image")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lifeofpix_creative_search(self):
        p = LifeOfPixProvider()
        res = p.search("drone coastline 4k nature", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "lifeofpix")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_flickr_commons_heritage_search(self):
        p = FlickrCommonsProvider()
        res = p.search("astronomy vintage telescope 1920", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "flickr_commons")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lazy_registry_52_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertEqual(len(avail), 52, f"Expected 52 available providers in registry, found {len(avail)}")
        for name in ["reshot", "lifeofpix", "flickr_commons"]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
