"""
Unit tests for ultimate media providers in CutWire Drift AI:
Prelinger Archives, British Library, Kaboompics, Mauritshuis Museum, and Videezy.
Validates the full expansion to 41 global providers.
"""
import unittest
from providers.prelinger import PrelingerProvider
from providers.british_library import BritishLibraryProvider
from providers.kaboompics import KaboompicsProvider
from providers.mauritshuis import MauritshuisProvider
from providers.videezy import VideezyProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestUltimateMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            PrelingerProvider(),
            BritishLibraryProvider(),
            KaboompicsProvider(),
            MauritshuisProvider(),
            VideezyProvider()
        ]
        expected_names = {"prelinger", "british_library", "kaboompics", "mauritshuis", "videezy"}
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_prelinger_archives_search(self):
        prelinger = PrelingerProvider()
        results = prelinger.search("retro vintage metropolis", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "prelinger")
        self.assertEqual(res.media_type, "video")
        self.assertIn("Public Domain", res.license)
        self.assertEqual(res.copyright_risk, "safe")
        self.assertTrue(res.commercial_use)

    def test_british_library_heritage_search(self):
        bl = BritishLibraryProvider()
        results = bl.search("ancient medieval cartography", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "british_library")
        self.assertEqual(res.media_type, "image")
        self.assertIn("Public Domain", res.license)
        self.assertEqual(res.copyright_risk, "safe")
        self.assertTrue(res.commercial_use)

    def test_kaboompics_aesthetic_search(self):
        kaboom = KaboompicsProvider()
        results = kaboom.search("scandinavian minimalist interior", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "kaboompics")
        self.assertEqual(res.media_type, "image")
        self.assertIn("Kaboompics", res.license)
        self.assertEqual(res.copyright_risk, "safe")
        self.assertTrue(res.commercial_use)

    def test_mauritshuis_masterpiece_search(self):
        mauritshuis = MauritshuisProvider()
        results = mauritshuis.search("vermeer pearl baroque painting", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "mauritshuis")
        self.assertEqual(res.media_type, "image")
        self.assertIn("CC0", res.license)
        self.assertEqual(res.copyright_risk, "safe")
        self.assertTrue(res.commercial_use)

    def test_videezy_broll_search(self):
        videezy = VideezyProvider()
        results = videezy.search("aerial ocean drone 4k", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "videezy")
        self.assertEqual(res.media_type, "video")
        self.assertIn("Videezy", res.license)
        self.assertEqual(res.copyright_risk, "safe")
        self.assertTrue(res.commercial_use)

    def test_lazy_registry_41_providers_resolution(self):
        avail = LazyProviderRegistry.available_providers()
        self.assertEqual(len(avail), 41, f"Expected 41 available providers in registry, found {len(avail)}")
        for name in ["prelinger", "british_library", "kaboompics", "mauritshuis", "videezy"]:
            self.assertIn(name, avail)
            inst = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(inst)
            self.assertEqual(inst.name, name)

if __name__ == "__main__":
    unittest.main()
