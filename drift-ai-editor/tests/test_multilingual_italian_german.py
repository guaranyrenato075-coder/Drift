"""
Unit tests for Italian and German multilingual support in CutWire Drift AI.
Verifies script generation, neural voice resolution, and MP4 multi-audio packing.
"""
import unittest
import os
import sys

from analysis.script_generator import ScriptGenerator
from voice.local_neural_fallback import LocalNeuralVoiceFallback
from pipeline.multilingual_audio_packager import MultilingualAudioPackager
from models.scene_plan import Scene, SceneState

class TestMultilingualItalianGerman(unittest.TestCase):

    def test_script_generator_italian(self):
        """Verifies script generation in authentic Italian."""
        script_it = ScriptGenerator.generate(topic="tecnologia", language="it")
        self.assertIn("SCENA 01", script_it)
        self.assertIn("NARRAZIONE", script_it)
        self.assertIn("DESCRIZIONE VISIVA", script_it)
        self.assertIn("DURATA: automatica", script_it)
        self.assertIn("intelligenza artificiale", script_it.lower())

    def test_script_generator_german(self):
        """Verifies script generation in authentic German."""
        script_de = ScriptGenerator.generate(topic="tecnologia", language="de")
        self.assertIn("SZENE 01", script_de)
        self.assertIn("SPRECHERTEXT", script_de)
        self.assertIn("VISUELLE BESCHREIBUNG", script_de)
        self.assertIn("DAUER: automatisch", script_de)
        self.assertIn("künstliche intelligenz", script_de.lower())

    def test_local_neural_voice_profiles_italian_and_german(self):
        """Verifies neural voice tone profiles for Italian and German."""
        profiles = LocalNeuralVoiceFallback.VOICE_PROFILES
        self.assertIn("it_documentary_deep", profiles)
        self.assertIn("it_expressive_female", profiles)
        self.assertIn("de_documentary_deep", profiles)
        self.assertIn("de_narrator_dynamic", profiles)

        self.assertEqual(profiles["it_documentary_deep"].gender, "male")
        self.assertEqual(profiles["it_expressive_female"].gender, "female")
        self.assertEqual(profiles["de_documentary_deep"].gender, "male")
        self.assertEqual(profiles["de_narrator_dynamic"].gender, "male")

        # Test automatic profile resolution
        scene_it = Scene(order=1, narration_text="Testo italiano", language="it")
        self.assertEqual(LocalNeuralVoiceFallback.resolve_profile_for_scene(scene_it), "it_documentary_deep")

        scene_de = Scene(order=2, narration_text="Deutscher Text", language="de")
        self.assertEqual(LocalNeuralVoiceFallback.resolve_profile_for_scene(scene_de), "de_documentary_deep")

    def test_multilingual_audio_packager_italian_and_german(self):
        """Verifies MP4 multi-audio multiplexing with Italian (ita) and German (deu)."""
        mapping = MultilingualAudioPackager.LANGUAGE_MAP
        self.assertIn("it", mapping)
        self.assertEqual(mapping["it"], ("ita", "Italiano"))
        self.assertIn("de", mapping)
        self.assertEqual(mapping["de"], ("deu", "Deutsch"))

        spec = MultilingualAudioPackager.create_multilingual_spec(
            project_id="test_it_de",
            video_path="d:/CUTWIREDRIFT/video.mp4",
            audio_tracks=[
                {"language": "pt", "title": "Português", "file_path": "d:/CUTWIREDRIFT/audio_pt.mp3", "is_default": True},
                {"language": "it", "title": "Italiano", "file_path": "d:/CUTWIREDRIFT/audio_it.mp3"},
                {"language": "de", "title": "Deutsch", "file_path": "d:/CUTWIREDRIFT/audio_de.mp3"}
            ]
        )

        self.assertEqual(len(spec.tracks), 3)
        self.assertEqual(spec.tracks[1].language_code, "ita")
        self.assertEqual(spec.tracks[2].language_code, "deu")

        # Verifica argumentos do FFmpeg com metadata
        cmd_str = " ".join(spec.ffmpeg_command_args)
        self.assertIn("language=ita", cmd_str)
        self.assertIn("language=deu", cmd_str)
        self.assertIn("handler_name=Italiano", cmd_str)
        self.assertIn("handler_name=Deutsch", cmd_str)

if __name__ == "__main__":
    unittest.main()
