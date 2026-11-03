import unittest
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, ProjectPlan, ProjectConfig, MediaCandidate
from editing.captions import CaptionManager
from editing.timeline_builder import TimelineBuilder
from editing.export_manager import ExportManager

class TestTimelineBuilder(unittest.TestCase):

    def test_caption_cues_and_srt(self):
        s1 = Scene(order=1, narration_text="Primeira linha narrada.", duration=4.0)
        s2 = Scene(order=2, narration_text="Segunda linha com mais texto.", duration=3.5)
        scenes = [s1, s2]
        
        # Test cues format
        cues = CaptionManager.build_subtitle_cues(scenes)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["in"], 0.0)
        self.assertEqual(cues[0]["out"], 4.0)
        self.assertEqual(cues[0]["text"], "Primeira linha narrada.")

        # Test SRT export
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tf:
            srt_path = Path(tf.name)

        try:
            CaptionManager.export_srt(scenes, srt_path)
            content = srt_path.read_text(encoding="utf-8")
            self.assertIn("00:00:00,000 --> 00:00:04,000", content)
            self.assertIn("Primeira linha narrada.", content)
        finally:
            srt_path.unlink(missing_ok=True)

    def test_timeline_builder_ops(self):
        mock_client = MagicMock()
        mock_client.apply.return_value = {
            "ok": True,
            "done": [{"result": {"assets": [{"name": "fake_video.mp4", "id": "asset-1"}]}}]
        }
        mock_client.inspect.return_value = {
            "tracks": [{"type": "video", "index": 0}, {"type": "audio", "index": 1}]
        }

        builder = TimelineBuilder(mock_client)
        plan = ProjectPlan(title="Projeto Montagem")
        s = Scene(
            order=1,
            narration_text="Texto",
            duration=5.0,
            selected_media=MediaCandidate(platform="pexels", external_id="1", local_cached_path="fake_video.mp4")
        )
        plan.scenes.append(s)

        res = builder.build_timeline(plan)
        self.assertTrue(res["ok"])
        self.assertEqual(res["scenes_placed"], 1)
        self.assertTrue(mock_client.apply.called)

if __name__ == "__main__":
    unittest.main()

