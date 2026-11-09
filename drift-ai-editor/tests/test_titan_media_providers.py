"""
Unit tests for titan expansion media providers in CutWire Drift AI:
SMK Open (National Gallery of Denmark), DPLA, U.S. Fish & Wildlife Service (USFWS),
Skitterphoto, FOCA Stock, Stockvault, and Trove (National Library of Australia).
Validates the milestone expansion to 65 global providers.
"""
import unittest
from providers.smk import SmkProvider
from providers.dpla import DplaProvider
from providers.usfws import UsfwsProvider
from providers.skitterphoto import SkitterphotoProvider
from providers.foca_stock import FocaStockProvider
from providers.stockvault import StockvaultProvider
from providers.trove import TroveProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestTitanMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            SmkProvider(),
            DplaProvider(),
            UsfwsProvider(),
            SkitterphotoProvider(),
            FocaStockProvider(),
            StockvaultProvider(),
            TroveProvider()
        ]
        expected_names = {
            "smk", "dpla", "usfws", "skitterphoto",
            "foca_stock", "stockvault", "trove"
        }
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_smk_nordic_masterpiece_search(self):
        p = SmkProvider()
        res = p.search("danish landscape copenhagen", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "smk")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_dpla_american_archive_search(self):
        p = DplaProvider()
        res = p.search("american revolution declaration", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "dpla")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_usfws_wildlife_search(self):
        p = UsfwsProvider()
        res = p.search("bald eagle river salmon", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "usfws")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_skitterphoto_cc0_search(self):
        p = SkitterphotoProvider()
        res = p.search("misty forest morning sunlight", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "skitterphoto")
        self.assertEqual(item.media_type, "image")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_foca_stock_workspace_search(self):
        p = FocaStockProvider()
        res = p.search("workspace laptop coffee code", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "foca_stock")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_stockvault_creative_search(self):
        p = StockvaultProvider()
        res = p.search("abstract 3d background texture", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "stockvault")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_trove_oceanic_heritage_search(self):
        p = TroveProvider()
        res = p.search("sydney harbour maritime vintage", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "trove")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lazy_registry_65_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertGreaterEqual(len(avail), 65, f"Expected at least 65 available providers in registry, found {len(avail)}")
        for name in [
            "smk", "dpla", "usfws", "skitterphoto",
            "foca_stock", "stockvault", "trove"
        ]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
