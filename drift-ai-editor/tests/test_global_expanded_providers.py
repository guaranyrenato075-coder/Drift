"""
Unit tests for globally expanded media providers in CutWire Drift AI:
Burst (Shopify), NYPL Digital Collections, V&A Museum, SplitShire, Picjumbo,
ISO Republic, Gratisography, and Yale University Art Gallery.
Validates the full expansion to 49 global providers.
"""
import unittest
from providers.burst import BurstProvider
from providers.nypl import NyplProvider
from providers.vam import VamProvider
from providers.splitshire import SplitShireProvider
from providers.picjumbo import PicjumboProvider
from providers.isorepublic import IsoRepublicProvider
from providers.gratisography import GratisographyProvider
from providers.yale import YaleProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestGlobalExpandedProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            BurstProvider(),
            NyplProvider(),
            VamProvider(),
            SplitShireProvider(),
            PicjumboProvider(),
            IsoRepublicProvider(),
            GratisographyProvider(),
            YaleProvider()
        ]
        expected_names = {
            "burst", "nypl", "vam", "splitshire",
            "picjumbo", "isorepublic", "gratisography", "yale"
        }
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_burst_commercial_search(self):
        p = BurstProvider()
        res = p.search("business startup tech", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "burst")
        self.assertEqual(item.media_type, "image")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_nypl_historical_search(self):
        p = NyplProvider()
        res = p.search("vintage new york 1900", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "nypl")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_vam_museum_search(self):
        p = VamProvider()
        res = p.search("renaissance sculpture design", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "vam")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Open Access", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_splitshire_cinematic_search(self):
        p = SplitShireProvider()
        res = p.search("drone mountain road", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "splitshire")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_picjumbo_stock_search(self):
        p = PicjumboProvider()
        res = p.search("modern coffee lifestyle", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "picjumbo")
        self.assertEqual(item.media_type, "image")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_isorepublic_curated_search(self):
        p = IsoRepublicProvider()
        res = p.search("urban architecture sunset", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "isorepublic")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_gratisography_quirky_hook_search(self):
        p = GratisographyProvider()
        res = p.search("funny creative surprise hook", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "gratisography")
        self.assertEqual(item.media_type, "image")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_yale_masterpiece_search(self):
        p = YaleProvider()
        res = p.search("philosophy antiquity classical", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "yale")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lazy_registry_49_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertGreaterEqual(len(avail), 49, f"Expected at least 49 available providers in registry, found {len(avail)}")
        for name in [
            "burst", "nypl", "vam", "splitshire",
            "picjumbo", "isorepublic", "gratisography", "yale"
        ]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
