import unittest
import os
import shutil
import tempfile
from core.desktop_launcher_daemon_packager import DesktopLauncherDaemonPackager


class TestDesktopLauncherDaemonPackager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_windows_batch_launcher(self):
        bat = DesktopLauncherDaemonPackager.generate_windows_batch_launcher("C:\\FakeApp", port=8765)
        self.assertIn("DRIFT AI CINEMATIC STUDIO", bat)
        self.assertIn("start http://localhost:8765", bat)

    def test_generate_powershell_launcher(self):
        ps1 = DesktopLauncherDaemonPackager.generate_powershell_launcher("C:\\FakeApp", port=8765)
        self.assertIn("Get-NetTCPConnection", ps1)
        self.assertIn("http://localhost:8765", ps1)

    def test_deploy_desktop_launchers(self):
        res = DesktopLauncherDaemonPackager.deploy_desktop_launchers(self.temp_dir, port=8765)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["batch_launcher"]))
        self.assertTrue(os.path.exists(res["powershell_launcher"]))


if __name__ == "__main__":
    unittest.main()
