import unittest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, ProjectPlan, MediaCandidate, Provenance
from providers import (
    PexelsProvider,
    PixabayProvider,
    WikimediaProvider,
    NasaProvider,
    UnsplashProvider,
    CoverrProvider,
    FreesoundProvider,
    ArchiveOrgProvider,
    OpenverseProvider,
    MetMuseumProvider,
    ArtInstituteChicagoProvider,
    SmithsonianProvider,
    LibraryOfCongressProvider,
    EuropeanaProvider,
    FreeMusicArchiveProvider,
    MixkitProvider,
    RijksmuseumProvider,
    ClevelandArtProvider,
    WellcomeCollectionProvider,
    BiodiversityProvider,
    UsgsProvider,
    NoaaProvider,
    JamendoMusicProvider,
    CcMixterProvider,
    IncompetechProvider,
    RawpixelProvider
)
from media.cache import MediaCache
from media.validator import MediaValidator
from media.attribution import AttributionManager

class TestProvidersAndMedia(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name) / "cache"
        self.cache = MediaCache(self.cache_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("urllib.request.urlopen")
    def test_pexels_provider_search(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""{
            "videos": [
                {
                    "id": 9991,
                    "width": 1920,
                    "height": 1080,
                    "duration": 6,
                    "image": "https://images.pexels.com/preview.jpg",
                    "url": "https://pexels.com/video/9991",
                    "user": {"name": "Alice Film"},
                    "video_files": [
                        {"file_type": "video/mp4", "width": 1920, "height": 1080, "link": "https://pexels.com/download/9991.mp4"}
                    ]
                }
            ]
        }"""
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        provider = PexelsProvider(api_key="fake-key")
        candidates = provider.search(query="storm rain", per_page=1)

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.platform, "pexels")
        self.assertEqual(c.external_id, "9991")
        self.assertEqual(c.creator, "Alice Film")
        self.assertEqual(c.download_url, "https://pexels.com/download/9991.mp4")
        self.assertEqual(c.duration, 6.0)

    @patch("urllib.request.urlopen")
    def test_pixabay_provider_search(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""{
            "hits": [
                {
                    "id": 8882,
                    "duration": 8,
                    "tags": "nature, trees, forest",
                    "pageURL": "https://pixabay.com/videos/8882",
                    "user": "Bob Creator",
                    "videos": {
                        "large": {"url": "https://pixabay.com/download/8882.mp4", "width": 1920, "height": 1080}
                    }
                }
            ]
        }"""
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        provider = PixabayProvider(api_key="fake-key")
        candidates = provider.search(query="forest", per_page=1)

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.platform, "pixabay")
        self.assertEqual(c.external_id, "8882")
        self.assertEqual(c.creator, "Bob Creator")
        self.assertEqual(c.download_url, "https://pixabay.com/download/8882.mp4")

    @patch("urllib.request.urlopen")
    def test_unsplash_provider_search(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""{
            "results": [
                {
                    "id": "unsp-101",
                    "width": 3840,
                    "height": 2160,
                    "alt_description": "Mountain peak sunrise",
                    "urls": {"regular": "https://images.unsplash.com/photo-101", "small": "https://images.unsplash.com/thumb-101"},
                    "user": {"name": "Clara Lens", "links": {"html": "https://unsplash.com/@clara"}},
                    "links": {"html": "https://unsplash.com/photos/unsp-101"}
                }
            ]
        }"""
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        provider = UnsplashProvider(api_key="fake-key")
        candidates = provider.search(query="mountain sunrise", per_page=1, media_type="image")

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.platform, "unsplash")
        self.assertEqual(c.external_id, "unsp-101")
        self.assertEqual(c.creator, "Clara Lens")
        self.assertEqual(c.download_url, "https://images.unsplash.com/photo-101")

    @patch("urllib.request.urlopen")
    def test_coverr_provider_search(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""{
            "hits": [
                {
                    "id": "cov-202",
                    "title": "Ocean Waves Drone",
                    "urls": {"mp4": "https://coverr.co/download/ocean.mp4", "thumbnail": "https://coverr.co/thumb.jpg"},
                    "author": {"name": "Dan Drone"},
                    "duration": 12.5,
                    "width": 1920,
                    "height": 1080
                }
            ]
        }"""
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        provider = CoverrProvider(api_key="fake-key")
        candidates = provider.search(query="ocean waves", per_page=1, media_type="video")

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.platform, "coverr")
        self.assertEqual(c.external_id, "cov-202")
        self.assertEqual(c.creator, "Dan Drone")
        self.assertEqual(c.download_url, "https://coverr.co/download/ocean.mp4")

    @patch("urllib.request.urlopen")
    def test_archive_org_provider_search(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"""{
            "response": {
                "docs": [
                    {
                        "identifier": "Apollo11_Mission_Highlights",
                        "title": "Apollo 11 Mission Highlights",
                        "description": "Historical moon landing footage",
                        "mediatype": "movies"
                    }
                ]
            }
        }"""
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        provider = ArchiveOrgProvider()
        candidates = provider.search(query="moon landing", per_page=1)

        self.assertEqual(len(candidates), 1)
        c = candidates[0]
        self.assertEqual(c.platform, "archive_org")
        self.assertEqual(c.external_id, "Apollo11_Mission_Highlights")
        self.assertIn("archive.org", c.download_url)

    def test_media_cache(self):
        target = self.cache.get_target_path("pexels", "123", "https://example.com/v.mp4")
        self.assertFalse(target.exists())

        target.write_bytes(b"0" * 2048)
        cached = self.cache.get_cached_file("pexels", "123", "https://example.com/v.mp4")
        self.assertIsNotNone(cached)
        self.assertEqual(cached, target)

    def test_media_validator(self):
        test_file = Path(self.temp_dir.name) / "sample.mp4"
        test_file.write_bytes(b"fake video data" * 500)

        valid, msg = MediaValidator.validate_file(test_file)
        self.assertTrue(valid)

        empty_file = Path(self.temp_dir.name) / "empty.mp4"
        empty_file.write_bytes(b"")
        valid, msg = MediaValidator.validate_file(empty_file)
        self.assertFalse(valid)
        self.assertIn("incompleto", msg)

    def test_attribution_report_generation(self):
        plan = ProjectPlan(title="Projeto Documentário")
        s = Scene(order=1, narration_text="Texto da cena", duration=4.5)
        s.provenance = Provenance(
            platform="pexels",
            item_id="9991",
            creator="Alice Film",
            license="Pexels License",
            page_url="https://pexels.com/video/9991",
            query="storm",
            local_path="C:/cache/pexels_9991.mp4"
        )
        plan.scenes.append(s)

        report = AttributionManager.generate_report(plan)
        self.assertIn("Alice Film", report)
        self.assertIn("Pexels License", report)
        self.assertIn("https://pexels.com/video/9991", report)


    @patch("urllib.request.urlopen")
    def test_openverse_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"results": [{"url": "https://img.openverse.org/1.jpg", "creator": "Jane", "title": "Lake"}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = OpenverseProvider()
        res = p.search("nature")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "openverse")
        self.assertEqual(res[0].creator, "Jane")

    @patch("urllib.request.urlopen")
    def test_artic_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": [{"id": 101, "image_id": "abc-123", "title": "The Bedroom", "artist_display": "Van Gogh"}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = ArtInstituteChicagoProvider()
        res = p.search("van gogh")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "artic")
        self.assertIn("abc-123", res[0].download_url)

    @patch("urllib.request.urlopen")
    def test_smithsonian_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": {"rows": [{"id": "si_1", "title": "Moon Rock", "content": {"descriptiveNonRepeating": {"online_media": {"media": [{"content": "https://si.edu/img.jpg"}]}}}}]}}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = SmithsonianProvider()
        res = p.search("moon")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "smithsonian")

    @patch("urllib.request.urlopen")
    def test_loc_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"results": [{"title": "Historic Photo", "image_url": ["https://loc.gov/1_thumb.jpg", "https://loc.gov/1_large.jpg"], "contributor": ["LOC Archive"]}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = LibraryOfCongressProvider()
        res = p.search("history")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "loc")

    @patch("urllib.request.urlopen")
    def test_europeana_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"items": [{"title": ["Ancient Map"], "edmPreview": ["https://europeana.eu/preview.jpg"], "dataProvider": ["British Library"]}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = EuropeanaProvider()
        res = p.search("map")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "europeana")

    @patch("urllib.request.urlopen")
    def test_mixkit_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": [{"video_url": "https://mixkit.co/download/123.mp4", "title": "Drone City", "duration": 10}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = MixkitProvider()
        res = p.search("drone")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "mixkit")


    @patch("urllib.request.urlopen")
    def test_rijksmuseum_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"artObjects": [{"objectNumber": "SK-A-3262", "title": "Night Watch", "webImage": {"url": "https://lh3.googleusercontent.com/1.jpg", "width": 2500, "height": 2000}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = RijksmuseumProvider()
        res = p.search("rembrandt")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "rijksmuseum")

    @patch("urllib.request.urlopen")
    def test_cleveland_art_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"data": [{"id": 1234, "title": "Greek Vase", "images": {"web": {"url": "https://clevelandart.org/1.jpg"}}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = ClevelandArtProvider()
        res = p.search("greek")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "cleveland_art")

    @patch("urllib.request.urlopen")
    def test_wellcome_collection_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"results": [{"id": "w123", "thumbnail": {"url": "https://wellcome.org/1.jpg"}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = WellcomeCollectionProvider()
        res = p.search("anatomy")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "wellcome_collection")

    @patch("urllib.request.urlopen")
    def test_jamendo_music_provider(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"results": [{"id": 555, "name": "Chill Beat", "audio": "https://jamendo.com/track.mp3", "artist_name": "Lofi Beats", "duration": 150}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        p = JamendoMusicProvider()
        res = p.search("lofi")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].platform, "jamendo")

    def test_curated_providers(self):
        p_usgs = UsgsProvider()
        self.assertEqual(len(p_usgs.search("earth", per_page=2)), 2)

        p_noaa = NoaaProvider()
        self.assertEqual(len(p_noaa.search("ocean", per_page=2)), 2)

        p_incompetech = IncompetechProvider()
        self.assertEqual(len(p_incompetech.search("suspense", per_page=2)), 2)

        p_rawpixel = RawpixelProvider()
        self.assertEqual(len(p_rawpixel.search("vintage", per_page=2)), 2)

if __name__ == "__main__":
    unittest.main()
