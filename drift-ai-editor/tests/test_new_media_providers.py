"""
Unit tests for new media providers in CutWire Drift AI:
Mazwai, ESA, DVIDS, CERN, and Videvo.
"""
import unittest
from providers.mazwai import MazwaiProvider
from providers.esa import EsaProvider
from providers.dvids import DvidsProvider
from providers.cern import CernProvider
from providers.videvo import VidevoProvider
from providers.base import BaseMediaProvider
from core.lazy_provider_registry import LazyProviderRegistry

class TestNewMediaProviders(unittest.TestCase):

    def test_providers_inheritance_and_names(self):
        providers = [
            MazwaiProvider(),
            EsaProvider(),
            DvidsProvider(),
            CernProvider(),
            VidevoProvider()
        ]
        expected_names = {"mazwai", "esa", "dvids", "cern", "videvo"}
        for p in providers:
            self.assertIsInstance(p, BaseMediaProvider)
            self.assertIn(p.name, expected_names)

    def test_mazwai_cinematic_search(self):
        mazwai = MazwaiProvider()
        results = mazwai.search("nature timelapse", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "mazwai")
        self.assertEqual(res.media_type, "video")
        self.assertEqual(res.aspect_ratio, "16:9")
        self.assertTrue(res.download_url.endswith(".mp4"))
        self.assertEqual(res.copyright_risk, "safe")

    def test_esa_astrophysics_search(self):
        esa = EsaProvider()
        results = esa.search("james webb galaxy", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "esa")
        self.assertIn("ESA", res.creator)
        self.assertEqual(res.copyright_risk, "safe")

    def test_dvids_aerospace_search(self):
        dvids = DvidsProvider()
        results = dvids.search("aerospace engineering", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "dvids")
        self.assertIn("Public Domain", res.license)
        self.assertEqual(res.copyright_risk, "safe")

    def test_cern_particle_physics_search(self):
        cern = CernProvider()
        results = cern.search("hadron collider quantum", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "cern")
        self.assertIn("CERN", res.creator)
        self.assertEqual(res.copyright_risk, "safe")

    def test_videvo_stock_footage_search(self):
        videvo = VidevoProvider()
        results = videvo.search("technology digital", per_page=3)
        self.assertGreaterEqual(len(results), 1)
        res = results[0]
        self.assertEqual(res.platform, "videvo")
        self.assertEqual(res.media_type, "video")
        self.assertEqual(res.copyright_risk, "safe")

    def test_lazy_registry_loads_new_providers(self):
        for name in ["mazwai", "esa", "dvids", "cern", "videvo"]:
            p = LazyProviderRegistry.get_provider(name)
            self.assertIsNotNone(p)
            self.assertEqual(p.name, name)

if __name__ == "__main__":
    unittest.main()
