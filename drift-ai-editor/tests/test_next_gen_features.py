import unittest
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, ProjectPlan, ProjectConfig, MediaCandidate
from editing.bidirectional_timeline import BidirectionalTimelineSync
from editing.zero_render_cache import ZeroRenderChunkCache
from director.voice_copilot import VoiceCopilotDirector
from analysis.channel_dna import ChannelDnaExtractor
from editing.dynamic_soundtrack import DynamicSoundtrackEngine
from editing.feed_simulator import FeedSimulator
from voice.speech_cleaner import SpeechCleaner
from editing.b_roll_generator import BRollDirector
from pipeline.direct_publisher import DirectPublisher
from pipeline.longform_documentary import LongformDocumentaryEngine

class TestNextGenFeatures(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_bidirectional_timeline_sync(self):
        plan = ProjectPlan(title="Sync Test")
        plan.scenes = [
            Scene(order=1, narration_text="Primeira frase", duration=4.0),
            Scene(order=2, narration_text="Segunda frase mais longa", duration=6.0)
        ]
        anchors = BidirectionalTimelineSync.index_script(plan)
        self.assertEqual(len(anchors), 2)
        self.assertEqual(anchors[0].timeline_in_us, 0)
        self.assertEqual(anchors[0].timeline_out_us, 4_000_000)
        self.assertEqual(anchors[1].timeline_in_us, 4_000_000)

        # Test char offset to us
        us = BidirectionalTimelineSync.text_offset_to_timeline_us(anchors, 5)
        self.assertGreater(us, 0)
        self.assertLessEqual(us, 4_000_000)

        # Test text deletion crop
        ok = BidirectionalTimelineSync.delete_text_range(plan, 2, "mais longa")
        self.assertTrue(ok)
        self.assertEqual(plan.scenes[1].narration_text, "Segunda frase")
        self.assertLess(plan.scenes[1].duration, 6.0)

    def test_zero_render_cache(self):
        cache = ZeroRenderChunkCache(cache_dir=self.temp_path / "chunks")
        scene = Scene(order=1, narration_text="Cena 1", duration=4.0)
        h1 = cache.compute_scene_hash(scene)
        self.assertTrue(len(h1) > 0)

        dummy_chunk = self.temp_path / "raw_chunk.mp4"
        dummy_chunk.write_bytes(b"0" * 2048)
        cached = cache.register_rendered_chunk(scene, dummy_chunk)
        self.assertTrue(cache.is_chunk_ready(scene))

        plan = ProjectPlan(title="Cache Concat")
        plan.scenes = [scene]
        all_ready, manifest, missing = cache.generate_concat_manifest(plan)
        self.assertTrue(all_ready)
        self.assertEqual(len(missing), 0)

    def test_voice_copilot_director(self):
        plan = ProjectPlan(title="Voice Copilot")
        plan.scenes = [Scene(order=1, narration_text="Intro", duration=4.0)]
        res = VoiceCopilotDirector.execute_voice_command("Deixe a música mais baixa", plan)
        self.assertTrue(res.success)
        self.assertEqual(res.feedback_audio_cue, "action_completed")

    def test_channel_dna_extractor(self):
        presets = ChannelDnaExtractor.list_presets()
        self.assertGreater(len(presets), 1)

        vox = ChannelDnaExtractor.get_preset("vox")
        self.assertIsNotNone(vox)
        self.assertEqual(vox.target_genre, "investigative_journalism")
        self.assertEqual(vox.style_profile.transition_type, "hard_cut")

    def test_dynamic_soundtrack_engine(self):
        plan = ProjectPlan(title="Soundtrack Test")
        plan.scenes = [
            Scene(order=1, narration_text="Hook misterioso", duration=4.0),
            Scene(order=2, narration_text="A verdade fundamental finalmente revelada", duration=5.0),
            Scene(order=3, narration_text="E assim encontramos a paz e a conclusão", duration=4.0)
        ]
        soundtrack = DynamicSoundtrackEngine.generate_soundtrack_plan(plan)
        self.assertEqual(len(soundtrack.cues), 3)
        # Climax in scene 2 must have active climax_accent
        self.assertGreater(soundtrack.cues[1].climax_accent_gain_db, -20.0)

    def test_feed_simulator(self):
        # Test safe margins
        audit_safe = FeedSimulator.audit_feed_safety("tiktok", 400, 260, 48)
        self.assertTrue(audit_safe.passed_safe_zone)

        # Test collision violation (too low)
        audit_clash = FeedSimulator.audit_feed_safety("tiktok", 400, 100, 24)
        self.assertFalse(audit_clash.passed_safe_zone)
        self.assertGreater(len(audit_clash.violations), 0)

    def test_speech_cleaner(self):
        report = SpeechCleaner.analyze_and_clean_speech("voice.wav", 12.0)
        self.assertGreater(report.detected_breaths_count, 0)
        self.assertLess(report.cleaned_duration_sec, 12.0)

    def test_b_roll_director(self):
        plan = ProjectPlan(title="B-Roll Test")
        plan.scenes = [
            Scene(order=1, narration_text="Ele consultou um antigo livro na mesa", duration=5.0)
        ]
        schedule = BRollDirector.schedule_b_roll(plan)
        self.assertEqual(schedule.total_inserts, 1)
        self.assertEqual(schedule.inserts[0].trigger_keyword, "livro")
        self.assertEqual(schedule.inserts[0].track_index, 1)

    def test_direct_publisher(self):
        plan = ProjectPlan(title="Vídeo Sobre Produtividade")
        plan.scenes = [Scene(order=1, concept="Intro", narration_text="Intro", duration=5.0)]
        fake_vid = self.temp_path / "video_final.mp4"
        fake_vid.write_bytes(b"0" * 4096)

        manifest = DirectPublisher.stage_publication(plan, fake_vid, platform="youtube")
        self.assertTrue(manifest.is_ready_for_dispatch)
        self.assertEqual(manifest.target_platform, "youtube")
        self.assertIn("Produtividade", manifest.title)

    def test_longform_documentary_engine(self):
        plan = ProjectPlan(title="Império Romano: A Ascensão e Queda")
        plan.scenes = [Scene(order=i, narration_text=f"Frase {i}", duration=6.0) for i in range(1, 16)]

        doc = LongformDocumentaryEngine.structure_documentary(plan, scenes_per_act=5)
        self.assertEqual(doc.total_chapters, 3)
        self.assertIn("Capítulo 1", doc.chapters[0].title)
        self.assertIn("Capítulo 2", doc.chapters[1].title)
        self.assertGreater(doc.total_estimated_duration_min, 1.0)

if __name__ == "__main__":
    unittest.main()
