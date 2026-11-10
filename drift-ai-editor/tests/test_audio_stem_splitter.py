"""
Unit tests for AudioStemSplitter in Drift AI.
Verifies multi-track stem manifests, channel faders, and FFmpeg mixdown filter graph.
"""
import unittest
from audio.audio_stem_splitter import AudioStemSplitter, StemMixerManifest, AudioStemTrack
from models.scene_plan import ProjectPlan, Scene

class TestAudioStemSplitter(unittest.TestCase):

    def test_create_default_mixer_manifest(self):
        plan = ProjectPlan(title="Projeto Audio Stems")
        plan.scenes = [
            Scene(order=1, narration_text="Narração de teste.", audio_path="temp/audio_1.wav")
        ]
        manifest = AudioStemSplitter.create_default_mixer_manifest(plan)
        self.assertIsInstance(manifest, StemMixerManifest)
        self.assertEqual(len(manifest.tracks), 3)
        self.assertTrue(manifest.export_ready)

        track_ids = {t.stem_id for t in manifest.tracks}
        self.assertIn("stem_dialogue", track_ids)
        self.assertIn("stem_music", track_ids)
        self.assertIn("stem_sfx", track_ids)

    def test_generate_ffmpeg_stem_filter(self):
        plan = ProjectPlan(title="Teste")
        manifest = AudioStemSplitter.create_default_mixer_manifest(plan)
        filter_str = AudioStemSplitter.generate_ffmpeg_stem_filter(manifest)
        self.assertIn("volume=", filter_str)
        self.assertIn("amix=inputs=3", filter_str)

if __name__ == "__main__":
    unittest.main()
