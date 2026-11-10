import unittest
import os
import shutil
import tempfile
from editing.nle_timeline_xml_edl_exporter import NLETimelineXMLEdlExporter


class TestNLETimelineXMLEdlExporter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_scenes = [
            {"duration": 5.0, "clip_name": "intro.mp4", "concept": "Introdução futurista"},
            {"duration": 3.5, "clip_name": "broll.mp4", "concept": "B-Roll IA generativa"}
        ]

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_frames_to_timecode(self):
        tc = NLETimelineXMLEdlExporter._frames_to_timecode(90, fps=30.0)
        self.assertEqual(tc, "00:00:03:00")

    def test_export_edl_cmx3600(self):
        edl = NLETimelineXMLEdlExporter.export_edl_cmx3600(self.sample_scenes, fps=30.0)
        self.assertIn("TITLE: DRIFT_PROJECT_TIMELINE", edl)
        self.assertIn("001  DRIFT    V     C", edl)
        self.assertIn("FROM CLIP NAME: intro.mp4", edl)

    def test_export_fcp_xml(self):
        xml_res = NLETimelineXMLEdlExporter.export_fcp_xml("Meufilme", self.sample_scenes, fps=30.0)
        self.assertIn("<xmeml version=\"4\">", xml_res)
        self.assertIn("<name>Meufilme</name>", xml_res)
        self.assertIn("clipitem-1", xml_res)

    def test_export_all_formats(self):
        res = NLETimelineXMLEdlExporter.export_all_formats("ProjetoAlpha", self.sample_scenes, self.temp_dir, fps=30.0)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["files"]["cmx3600_edl"]))
        self.assertTrue(os.path.exists(res["files"]["premiere_davinci_xml"]))


if __name__ == "__main__":
    unittest.main()
