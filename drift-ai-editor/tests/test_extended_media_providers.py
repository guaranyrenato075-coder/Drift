"""
Unit tests for extended media providers in CutWire Drift AI:
NARA, Getty Open Content, Paris Musées, Dareful 4K, and National Gallery of Art (NGA).
"""
import unittest
from providers.nara import NaraProvider
from providers.getty_open import GettyOpenProvider
from providers.paris_musees import ParisMuseesProvider
from providers.dareful import DarefulProvider
from providers.nga import NgaProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestExtendedMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            NaraProvider(),
            GettyOpenProvider(),
            ParisMuseesProvider(),
            DarefulProvider(),
            NgaProvider()
        ]
        expected_names = {"nara", "getty_open", "paris_musees", "dareful", "nga"}
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_nara_historical_search(self):
        nara = NaraProvider()
        results = nara.search("world war aviation", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "nara")
        self.assertIn("NARA", res.creator)
        self.assertEqual(res.copyright_risk, "safe")
        self.assertIn("Public Domain", res.license)

    def test_getty_open_content_search(self):
        getty = GettyOpenProvider()
        results = getty.search("ancient sculpture", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "getty_open")
        self.assertEqual(res.media_type, "image")
        self.assertIn("CC0", res.license)
        self.assertEqual(res.copyright_risk, "safe")

    def test_paris_musees_search(self):
        paris = ParisMuseesProvider()
        results = paris.search("renaissance portrait", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "paris_musees")
        self.assertEqual(res.media_type, "image")
        self.assertIn("CC0", res.license)
        self.assertEqual(res.copyright_risk, "safe")

    def test_dareful_4k_cinema_search(self):
        dareful = DarefulProvider()
        results = dareful.search("nature sunset mountain", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "dareful")
        self.assertEqual(res.media_type, "video")
        self.assertEqual(res.width, 3840)
        self.assertEqual(res.height, 2160)
        self.assertIn("CC-BY", res.license)
        self.assertEqual(res.copyright_risk, "safe")

    def test_nga_masterpieces_search(self):
        nga = NgaProvider()
        results = nga.search("impressionism landscape", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "nga")
        self.assertEqual(res.media_type, "image")
        self.assertIn("Public Domain", res.license)
        self.assertEqual(res.copyright_risk, "safe")

    def test_lazy_registry_loads_extended_providers(self):
        for name in ["nara", "getty_open", "paris_musees", "dareful", "nga"]:
            p = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(p)
            self.assertEqual(p.name, name)

if __name__ == "__main__":
    unittest.main()
