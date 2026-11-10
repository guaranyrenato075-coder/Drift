"""
Unit tests for SocialMediaMultiExportPresets in CutWire Drift AI.
Verifies multi-channel export specifications and batch render manifest generation.
"""
import unittest
from pipeline.multi_export_orchestrator import SocialMediaMultiExportPresets
from models.scene_plan import ProjectPlan

class TestMultiExportOrchestrator(unittest.TestCase):

    def test_list_presets(self):
        presets = SocialMediaMultiExportPresets.list_presets()
        self.assertEqual(len(presets), 4)
        preset_ids = [p["preset_id"] for p in presets]
        self.assertIn("youtube_16_9", preset_ids)
        self.assertIn("shorts_reels_9_16", preset_ids)
        self.assertIn("feed_linkedin_1_1", preset_ids)
        self.assertIn("podcast_audio_mp3", preset_ids)

    def test_build_export_manifest_all(self):
        plan = ProjectPlan(title="Projeto Multi-Export")
        manifest = SocialMediaMultiExportPresets.build_export_manifest(plan)

        self.assertEqual(manifest["project_id"], plan.project_id)
        self.assertEqual(manifest["total_exports_planned"], 4)
        tasks = manifest["export_tasks"]
        self.assertEqual(len(tasks), 4)

        # Check MP3 audio task
        podcast_task = next(t for t in tasks if t["preset_id"] == "podcast_audio_mp3")
        self.assertTrue(podcast_task["output_file"].endswith(".mp3"))
        self.assertIn("-vn", podcast_task["ffmpeg_command"])

        # Check Shorts task
        shorts_task = next(t for t in tasks if t["preset_id"] == "shorts_reels_9_16")
        self.assertTrue(shorts_task["output_file"].endswith(".mp4"))
        self.assertEqual(shorts_task["aspect_ratio"], "9:16")

    def test_build_export_manifest_selective(self):
        plan = ProjectPlan(title="Projeto Seletivo")
        manifest = SocialMediaMultiExportPresets.build_export_manifest(plan, selected_ids=["youtube_16_9", "shorts_reels_9_16"])
        self.assertEqual(manifest["total_exports_planned"], 2)

if __name__ == '__main__':
    unittest.main()
