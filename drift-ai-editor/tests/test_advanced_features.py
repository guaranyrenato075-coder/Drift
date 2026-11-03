import unittest
import sys
import tempfile
import wave
import struct
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import Scene, ProjectPlan, ProjectConfig, MediaCandidate, Provenance
from pipeline.job_manager import JobManager, JobStage, JobStatus
from voice.audio_aligner import AudioAligner
from analysis.storyboard_engine import StoryboardEngine
from media.media_ranker import MediaRanker
from media.local_indexer import LocalMediaIndexer
from media.license_manifest import LicenseManifestManager
from pipeline.style_engine import StyleEngine
from pipeline.timeline_planner import TimelinePlanner
from pipeline.quality_control import QualityControlEngine

class TestAdvancedFeatures(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_job_manager_lifecycle(self):
        jm = JobManager(storage_dir=self.temp_path / "jobs")
        job = jm.create_job("proj_123")
        self.assertEqual(job.status, JobStatus.PENDING)

        jm.update_stage(job.job_id, JobStage.STORYBOARD, 20.0, "Storyboard criado", {"scenes_count": 5})
        reloaded = jm.get_job(job.job_id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.current_stage, JobStage.STORYBOARD)
        self.assertEqual(reloaded.progress, 20.0)
        self.assertTrue(jm.can_resume_stage(reloaded, JobStage.STORYBOARD))

        jm.complete_job(job.job_id)
        done = jm.get_job(job.job_id)
        self.assertEqual(done.status, JobStatus.COMPLETED)

    def test_audio_aligner_wav(self):
        # Create a synthetic 1-second WAV file (16-bit PCM, 44100Hz, mono)
        wav_path = self.temp_path / "test_voice.wav"
        rate = 44100
        duration = 1.0
        n_samples = int(rate * duration)
        with wave.open(str(wav_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            # 440 Hz sine wave samples
            samples = [int(10000 * (i % 100) / 100) for i in range(n_samples)]
            wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

        alignment = AudioAligner.align_narration(
            scene_order=1,
            narration_text="O medo de fracassar paralisa",
            audio_file_path=wav_path
        )
        self.assertAlmostEqual(alignment.total_duration, 1.0, places=1)
        self.assertEqual(len(alignment.words), 5)
        self.assertTrue(alignment.words[0].word == "O")
        self.assertFalse(alignment.has_clipping)

    def test_storyboard_engine(self):
        hooks = StoryboardEngine.generate_hooks("Estoicismo")
        self.assertEqual(len(hooks), 3)
        self.assertEqual(hooks[0].hook_type, "provocative")

        scene = Scene(order=1, narration_text="O medo de fracassar impede as pessoas de agir", visual_description="Pessoa hesitando")
        intent = StoryboardEngine.analyze_scene_intent(scene, 0, 1)
        self.assertEqual(intent.emotional_tone, "hesitation")
        self.assertIn("crossroads", intent.search_queries[0])

    def test_media_ranker(self):
        scene = Scene(order=1, narration_text="Espaço profundo", duration=5.0)
        c1 = MediaCandidate(platform="pexels", external_id="1", title="4K Space", creator="Artist A", download_url="url1", width=3840, height=2160, duration=8.0)
        c2 = MediaCandidate(platform="pixabay", external_id="2", title="HD Space", creator="Artist B", download_url="url2", width=1920, height=1080, duration=4.0)

        ranked = MediaRanker.rank_scene_candidates([c1, c2], scene, used_creators=[], used_external_ids=[], preferred_aspect="16:9")
        self.assertEqual(len(ranked), 2)
        # c1 has 4K and > duration, should rank first
        self.assertEqual(ranked[0].external_id, "1")

    def test_local_indexer(self):
        # Create dummy local video and image files
        sub = self.temp_path / "drone_nature"
        sub.mkdir()
        (sub / "mountain_sunset_4k.mp4").write_bytes(b"dummy")
        (sub / "calm_forest.jpg").write_bytes(b"dummy")

        indexer = LocalMediaIndexer(index_cache_path=self.temp_path / "idx.json")
        count = indexer.scan_directory(str(self.temp_path))
        self.assertEqual(count, 2)

        matches = indexer.search_local("mountain")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].platform, "local")

    def test_style_engine_and_safe_zones(self):
        profile = StyleEngine.get_profile("filosofico")
        self.assertEqual(profile.transition_type, "crossfade")

        # Test 9:16 vertical video safe zone
        vertical_safe = StyleEngine.adapt_for_aspect_ratio(profile, "9:16")
        self.assertEqual(vertical_safe["width"], 1080)
        self.assertEqual(vertical_safe["height"], 1920)
        self.assertGreater(vertical_safe["safe_zone_bottom"], 100)

    def test_timeline_planner_and_qc(self):
        plan = ProjectPlan(title="Projeto Filosofia", config=ProjectConfig())
        s1 = Scene(order=1, narration_text="Primeira frase", duration=4.0)
        plan.scenes.append(s1)

        # Before media & audio: QC should detect missing files
        report = QualityControlEngine.audit_project(plan)
        self.assertFalse(report.is_ready_for_export)
        self.assertGreater(report.errors_count, 0)

        # Attach valid dummy media & audio
        audio_dummy = self.temp_path / "audio1.wav"
        audio_dummy.write_bytes(b"dummy")
        media_dummy = self.temp_path / "video1.mp4"
        media_dummy.write_bytes(b"dummy")

        s1.audio_path = str(audio_dummy)
        s1.selected_media = MediaCandidate(
            platform="local", external_id="m1", title="Media 1",
            download_url="u1", local_cached_path=str(media_dummy)
        )

        assembly = TimelinePlanner.create_assembly_plan(plan)
        self.assertTrue(assembly.validation_passed)
        self.assertGreater(len(assembly.batches), 0)

    def test_license_manifest(self):
        plan = ProjectPlan(title="Doc Teste")
        s = Scene(order=1, narration_text="Test", duration=3.0)
        s.selected_media = MediaCandidate(
            platform="pexels", external_id="p10", title="Ocean", creator="Jane Cam",
            download_url="u1", page_url="https://pexels.com/video/p10", license="Pexels License"
        )
        plan.scenes.append(s)

        out_md = self.temp_path / "licenca.md"
        content = LicenseManifestManager.save_markdown_report(plan, out_md)
        self.assertIn("PEXELS", content)
        self.assertIn("Jane Cam", content)
        self.assertTrue(out_md.exists())

if __name__ == "__main__":
    unittest.main()
