import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, SceneState
from voice.voice_engine import DriftChatterboxEngine

class TestDriftChatterboxEngine(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.engine = DriftChatterboxEngine(self.mock_client)

    def test_check_status(self):
        self.mock_client.local_tts_status.return_value = {
            "ok": True,
            "available": True,
            "addon_id": "tts-model",
            "languages": [{"code": "pt", "label": "Portuguese"}, {"code": "en", "label": "English"}],
            "last_voice": "default",
            "last_exaggeration": 0.5,
            "model_loaded": True
        }

        status = self.engine.check_status()
        self.assertTrue(status["ok"])
        self.assertTrue(status["available"])
        self.assertEqual(len(status["languages"]), 2)
        self.assertEqual(status["languages"][0]["code"], "pt")

    def test_list_voices(self):
        self.mock_client.list_local_voices.return_value = [
            {"id": "default", "name": "Default", "built_in": True}
        ]
        voices = self.engine.list_voices()
        self.assertEqual(len(voices), 1)
        self.assertEqual(voices[0]["id"], "default")

    def test_generate_scene_success(self):
        scene = Scene(
            order=1,
            narration_text="Esta é uma frase de teste.",
            language="pt",
            voice_id="default",
            exaggeration=0.6
        )

        # Mock tts_generate response
        self.mock_client.tts_generate.return_value = {"job_id": "job-12345"}

        # Mock get_job response returning completion
        self.mock_client.get_job.return_value = {
            "active": False,
            "status": "completed",
            "ok": True,
            "result": {
                "path": "C:/fake/audio_scene_1.wav",
                "duration": 4.75
            }
        }

        result = self.engine.generate_scene(scene)

        self.mock_client.tts_generate.assert_called_once_with(
            text="Esta é uma frase de teste.",
            voice="default",
            language="pt",
            exaggeration=0.6,
            provider="local",
            place=False
        )
        self.assertEqual(result.state, SceneState.READY)
        self.assertEqual(result.audio_path, "C:/fake/audio_scene_1.wav")
        self.assertEqual(result.duration, 4.75)
        self.assertEqual(result.audio_duration, 4.75)

    def test_generate_scene_error_handling(self):
        scene = Scene(order=2, narration_text="Erro intencional.")
        self.mock_client.tts_generate.return_value = {"job_id": "job-fail"}
        self.mock_client.get_job.return_value = {
            "active": False,
            "status": "failed",
            "ok": False,
            "error": "Erro no modelo Chatterbox"
        }

        result = self.engine.generate_scene(scene)
        self.assertEqual(result.state, SceneState.ERROR)
        self.assertIn("Chatterbox", result.error_message)

    def test_regenerate_single_scene_preserves_others(self):
        s1 = Scene(order=1, narration_text="Cena 1 ok", state=SceneState.READY, audio_path="/a1.wav", duration=3.0)
        s2 = Scene(order=2, narration_text="Cena 2 para refazer", state=SceneState.PENDING)

        self.mock_client.tts_generate.return_value = {"job_id": "job-s2"}
        self.mock_client.get_job.return_value = {
            "active": False,
            "status": "completed",
            "result": {"path": "/a2.wav", "duration": 5.2}
        }

        self.engine.generate_scene(s2)

        # s2 updated
        self.assertEqual(s2.state, SceneState.READY)
        self.assertEqual(s2.audio_path, "/a2.wav")
        self.assertEqual(s2.duration, 5.2)

        # s1 preserved
        self.assertEqual(s1.state, SceneState.READY)
        self.assertEqual(s1.audio_path, "/a1.wav")
        self.assertEqual(s1.duration, 3.0)

if __name__ == "__main__":
    unittest.main()

