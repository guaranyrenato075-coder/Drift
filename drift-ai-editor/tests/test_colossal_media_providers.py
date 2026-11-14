"""
Unit tests for colossal 76-provider milestone in CutWire Drift AI:
Harvard Art Museums, American Archive of Public Broadcasting (AAPB),
Museum of New Zealand Te Papa Tongarewa, Minneapolis Institute of Art (Mia),
Barnimages, and Picryl / GetArchive.
Validates the milestone expansion to 76 global providers.
"""
import unittest
from providers.harvard_art import HarvardArtProvider
from providers.aapb import AapbProvider
from providers.te_papa import TePapaProvider
from providers.mia import MiaProvider
from providers.barnimages import BarnimagesProvider
from providers.picryl import PicrylProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestColossalMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            HarvardArtProvider(),
            AapbProvider(),
            TePapaProvider(),
            MiaProvider(),
            BarnimagesProvider(),
            PicrylProvider()
        ]
        expected_names = {"harvard_art", "aapb", "te_papa", "mia", "barnimages", "picryl"}
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_harvard_art_masterwork_search(self):
        p = HarvardArtProvider()
        res = p.search("renaissance portrait coin sculpture", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "harvard_art")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_aapb_broadcast_archive_search(self):
        p = AapbProvider()
        res = p.search("presidential address space broadcast", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "aapb")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_te_papa_pacific_heritage_search(self):
        p = TePapaProvider()
        res = p.search("maori carving pacific expedition", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "te_papa")
        self.assertEqual(item.media_type, "image")
        self.assertIn("CC0", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_mia_global_masterpiece_search(self):
        p = MiaProvider()
        res = p.search("asian ceramic textile ancient", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "mia")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_barnimages_authentic_search(self):
        p = BarnimagesProvider()
        res = p.search("travel espresso coffee morning", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "barnimages")
        self.assertEqual(item.media_type, "image")
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_picryl_public_domain_search(self):
        p = PicrylProvider()
        res = p.search("vintage astronomy telescope cosmos", per_page=3)
        self.assertGreaterEqual(len(res), 1)
        item = res[0]
        self.assertEqual(item.platform, "picryl")
        self.assertEqual(item.media_type, "image")
        self.assertIn("Public Domain", item.license)
        self.assertEqual(item.copyright_risk, "safe")
        self.assertTrue(item.commercial_use)

    def test_lazy_registry_76_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertEqual(len(avail), 76, f"Expected 76 available providers in registry, found {len(avail)}")
        for name in [
            "harvard_art", "aapb", "te_papa",
            "mia", "barnimages", "picryl"
        ]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
