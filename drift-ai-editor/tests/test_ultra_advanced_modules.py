"""
Unit and integration tests for ultra-advanced production modules:
MulticamDirector, CharacterContinuity, MediaDoctor, LipSyncAligner,
AccessibilityEngine, CitationDirector, ShotExtender, SoundscapeGenerator,
ProjectDiffMerge, ReviewBoard, DistributedRenderManager, HardwareProfiler.
"""
import unittest
from editing.multicam_director import MulticamDirector, CameraAngle
from analysis.character_continuity import CharacterContinuityTracker, CharacterPersona
from media.media_doctor import MediaDoctor
from voice.lip_sync_aligner import LipSyncAligner
from editing.accessibility_engine import AccessibilityEngine
from editing.academic_citations import CitationDirector, CitationReference
from editing.shot_extender import ShotExtender, ExtensionStrategy
from audio.soundscape_generator import SoundscapeGenerator, EnvironmentType
from core.project_diff_merge import ProjectDiffMerge
from collaboration.review_board import ReviewBoard, TaskType
from pipeline.distributed_render import DistributedRenderManager, RenderWorkerNode, ChunkStatus
from core.hardware_profiler import HardwareProfiler, HardwareTier

class TestUltraAdvancedModules(unittest.TestCase):

    def test_multicam_director(self):
        director = MulticamDirector()
        env1 = [0.1, 0.5, 0.9, 0.4, 0.1]
        env2 = [0.0, 0.1, 0.5, 0.9, 0.4]  # lagged by 1 sample
        offset = director.calculate_sync_offset(env1, env2, sample_rate=10.0)
        self.assertAlmostEqual(offset, 0.1, places=1)

        angles = [
            CameraAngle("cam1", "cam1.mp4", "Host"),
            CameraAngle("cam2", "cam2.mp4", "Guest")
        ]
        cuts = director.generate_multicam_edit(angles, total_duration=10.0)
        self.assertGreater(len(cuts), 1)
        self.assertEqual(cuts[0].active_camera_id, "cam1")
        self.assertEqual(cuts[1].active_camera_id, "cam2")

    def test_character_continuity(self):
        tracker = CharacterContinuityTracker()
        tracker.register_persona(CharacterPersona(
            character_id="hero",
            name="Anya",
            gender="Female",
            age_range="25yo",
            visual_signature="Cyberpunk runner with neon cyan hair",
            fixed_traits=["neon cyan hair", "silver jacket"]
        ))
        anchor = tracker.generate_prompt_anchor("hero")
        self.assertIn("Anya", anchor)
        self.assertIn("neon cyan hair", anchor)

        # Audit consistent scene
        res_ok = tracker.audit_scene(0, "hero", "Anya running with neon cyan hair and silver jacket in the rain")
        self.assertTrue(res_ok.is_consistent)

        # Audit inconsistent scene
        res_bad = tracker.audit_scene(1, "hero", "A girl with blonde hair in a hoodie")
        self.assertFalse(res_bad.is_consistent)
        self.assertEqual(len(res_bad.missing_traits), 2)

    def test_media_doctor(self):
        diag = MediaDoctor.inspect("dummy_clip.mp4", probe_info={
            "is_vfr": True,
            "sample_rate": 44100,
            "rotation": 90,
            "pix_fmt": "yuv422p"
        })
        # Since dummy_clip.mp4 doesn't exist on disk, inspect reports File not found
        self.assertFalse(diag.is_healthy)
        self.assertIn("File not found", diag.issues[0])

    def test_lip_sync_aligner(self):
        cue = LipSyncAligner.calculate_dub_alignment("cue_1", original_start=0.0, original_end=3.0, dubbed_natural_duration=3.6)
        self.assertTrue(cue.is_within_tolerances)
        self.assertIn("atempo", cue.ffmpeg_tempo_filter)

        visemes = LipSyncAligner.generate_viseme_track([(0.1, "AA"), (0.5, "M"), (0.9, "SIL")])
        self.assertEqual(len(visemes), 3)
        self.assertEqual(visemes[0].viseme, "O")
        self.assertEqual(visemes[1].viseme, "M")
        self.assertEqual(visemes[2].viseme, "rest")

    def test_accessibility_engine(self):
        subs = [
            {"text": "Short fast text that has way too many words for its duration", "start": 0.0, "end": 0.5, "text_rgb": (255, 255, 255), "bg_rgb": (0, 0, 0)},
            {"text": "Low contrast", "start": 1.0, "end": 3.0, "text_rgb": (100, 100, 100), "bg_rgb": (90, 90, 90)}
        ]
        report = AccessibilityEngine.audit_subtitles(subs, audio_pauses=[(5.0, 8.5)])
        self.assertEqual(report.total_subtitles, 2)
        self.assertEqual(report.wcag_fail_count, 1)
        self.assertEqual(len(report.reading_speed_violations), 1)
        self.assertEqual(len(report.audio_description_slots), 1)

    def test_academic_citations(self):
        director = CitationDirector()
        director.add_reference(CitationReference(
            ref_id="turing1950",
            authors="Turing, A. M.",
            year=1950,
            title="Computing Machinery and Intelligence",
            source_venue="Mind, 59(236)"
        ))
        overlay = director.schedule_overlay(0, 5.0, 4.0, "turing1950")
        self.assertIsNotNone(overlay)
        self.assertIn("Fonte: Turing, A. M.", overlay.formatted_lower_third)
        bib = director.export_apa_bibliography()
        self.assertEqual(len(bib), 1)
        self.assertIn("1950", bib[0])

    def test_shot_extender(self):
        plan_slowmo = ShotExtender.plan_extension("c1", current_duration=3.0, target_duration=3.6)
        self.assertEqual(plan_slowmo.strategy, ExtensionStrategy.OPTICAL_SLOWMO)

        plan_freeze = ShotExtender.plan_extension("c2", current_duration=2.0, target_duration=6.0)
        self.assertEqual(plan_freeze.strategy, ExtensionStrategy.KEN_BURNS_FREEZE)

        plan_loop = ShotExtender.plan_extension("c3", current_duration=2.0, target_duration=3.5, is_ambient_motion=True)
        self.assertEqual(plan_loop.strategy, ExtensionStrategy.PING_PONG_LOOP)

    def test_soundscape_generator(self):
        soundscape = SoundscapeGenerator.create_soundscape(EnvironmentType.CYBERPUNK)
        self.assertEqual(soundscape.environment, EnvironmentType.CYBERPUNK)
        self.assertGreaterEqual(len(soundscape.layers), 2)

        env = SoundscapeGenerator.detect_environment_from_text("As estrelas brilham no espaço infinito do cosmos")
        self.assertEqual(env, EnvironmentType.DEEP_SPACE)

    def test_project_diff_merge(self):
        base = {"s1": {"media_path": "a.mp4", "narration_text": "hello"}}
        branch_audio = {"s1": {"media_path": "a.mp4", "narration_text": "hello world revised"}}
        branch_visual = {"s1": {"media_path": "b_cinematic.mp4", "narration_text": "hello"}}

        merge_res = ProjectDiffMerge.merge_branches(base, branch_audio, branch_visual)
        self.assertTrue(merge_res.is_clean)
        self.assertEqual(merge_res.merged_project_state["s1"]["narration_text"], "hello world revised")
        self.assertEqual(merge_res.merged_project_state["s1"]["media_path"], "b_cinematic.mp4")

    def test_review_board(self):
        board = ReviewBoard()
        board.add_comment("Client", 12.5, "Trocar imagem para algo mais futurista")
        self.assertEqual(len(board.comments), 1)
        self.assertEqual(len(board.tasks), 1)
        self.assertEqual(board.tasks[0].task_type, TaskType.SWAP_MEDIA)
        board.mark_resolved(board.comments[0].comment_id)
        self.assertTrue(board.comments[0].is_resolved)
        self.assertEqual(board.tasks[0].status, "completed")

    def test_distributed_render(self):
        mgr = DistributedRenderManager(target_chunk_duration=10.0)
        mgr.register_worker(RenderWorkerNode("w1", "Local Worker", is_local=True, max_parallel_slots=2))
        chunks = mgr.partition_project([4.0, 4.0, 5.0, 3.0, 6.0])
        self.assertGreater(len(chunks), 1)

        c1 = mgr.schedule_next_chunk()
        self.assertIsNotNone(c1)
        self.assertEqual(c1.status, ChunkStatus.RENDERING)
        mgr.complete_chunk(c1.chunk_id)
        self.assertEqual(c1.status, ChunkStatus.COMPLETED)
        manifest = mgr.generate_concat_manifest()
        self.assertIn("file '", manifest)

    def test_hardware_profiler(self):
        profile = HardwareProfiler.probe()
        self.assertGreater(profile.cpu_cores, 0)
        self.assertGreater(profile.ram_gb, 0)
        self.assertIn(profile.hardware_tier, [HardwareTier.ENTRY, HardwareTier.STANDARD, HardwareTier.PRO])

if __name__ == "__main__":
    unittest.main()

