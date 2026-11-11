import unittest
from media.downloader import MediaDownloader
from models.scene_plan import MediaCandidate


class TestMediaDownloaderSecurity(unittest.TestCase):
    def test_blocks_file_scheme_ssrf(self):
        is_safe, reason = MediaDownloader.is_safe_download_url("file:///etc/passwd")
        self.assertFalse(is_safe)
        self.assertIn("Protocolo não permitido", reason)

    def test_blocks_localhost_loopback(self):
        is_safe, reason = MediaDownloader.is_safe_download_url("http://localhost:8765/api/health")
        self.assertFalse(is_safe)
        self.assertIn("Acesso bloqueado a endereço reservado ou interno", reason)

    def test_blocks_ip_loopback(self):
        is_safe, reason = MediaDownloader.is_safe_download_url("http://127.0.0.1:8765/api/health")
        self.assertFalse(is_safe)
        self.assertIn("Acesso bloqueado a endereço reservado ou interno", reason)

    def test_blocks_cloud_metadata(self):
        is_safe, reason = MediaDownloader.is_safe_download_url("http://169.254.169.254/latest/meta-data/")
        self.assertFalse(is_safe)
        self.assertIn("Acesso bloqueado", reason)

    def test_allows_public_https_media(self):
        is_safe, reason = MediaDownloader.is_safe_download_url("https://images.pexels.com/photos/1234/test.jpg")
        self.assertTrue(is_safe)
        self.assertEqual(reason, "URL segura")


if __name__ == "__main__":
    unittest.main()
