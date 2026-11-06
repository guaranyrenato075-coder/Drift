"""
Unit tests for CutWire Drift AI Long-Form Production Features:
1. LongFormRetentionDirector (Pattern interrupts, 3-act tension curves)
2. MultiChapterMoodSoundtrackOrchestrator (Mood crossfades & transitions)
3. SmartKenBurnsPunchInEngine (Dynamic motion & punch-in emphasis)
4. RenderCheckpointManager (Crash-proof rendering & resume)
"""
import unittest
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tempfile
import json
from models.scene_plan import Scene, SceneState
from director.long_form_retention_director import LongFormRetentionDirector, LongFormPacingStructure
from audio.multi_chapter_mood_soundtrack import MultiChapterMoodSoundtrackOrchestrator, MultiChapterAudioPlan
from editing.smart_ken_burns_punchin import SmartKenBurnsPunchInEngine, VisualMotionEffect
from pipeline.render_checkpoint_manager import RenderCheckpointManager, RenderCheckpointState

class TestLongFormInnovations(unittest.TestCase):

    def setUp(self):
        # Cria uma timeline simulada de 20 minutos (120 cenas de 10s = 1200s)
        self.long_scenes = []
        for i in range(1, 121):
            sc = Scene(
                order=i,
                narration_text=f"Esta é a narração detalhada da cena {i} trazendo informações relevantes sobre a história.",
                duration=10.0,
                keywords=["história", "documentário"]
            )
            self.long_scenes.append(sc)

    def test_long_form_retention_director_pacing(self):
        # 1200 segundos com gancho a cada 210s (3.5 min)
        pacing = LongFormRetentionDirector.structure_narrative_arc(self.long_scenes, target_interval_sec=210.0)
        
        self.assertEqual(pacing.total_scenes, 120)
        self.assertAlmostEqual(pacing.estimated_duration_sec, 1200.0)
        self.assertEqual(len(pacing.acts), 3)
        self.assertEqual(pacing.acts[0]["act_number"], 1)
        self.assertEqual(pacing.acts[1]["act_number"], 2)
        self.assertEqual(pacing.acts[2]["act_number"], 3)
        
        # Espera pelo menos 4 a 6 ganchos ao longo dos 20 minutos
        self.assertGreaterEqual(len(pacing.hooks_inserted), 4)
        self.assertGreaterEqual(pacing.retention_score, 80.0)

        # Testa aplicação direta nas cenas
        enriched = LongFormRetentionDirector.apply_hooks_to_scenes(self.long_scenes, target_interval_sec=210.0)
        self.assertEqual(len(enriched), 120)
        hooked_scenes = [s for s in enriched if any("hook:" in t for t in s.keywords)]
        self.assertGreaterEqual(len(hooked_scenes), 4)

    def test_multi_chapter_mood_soundtrack(self):
        total_dur = 1200.0 # 20 minutos
        plan = MultiChapterMoodSoundtrackOrchestrator.generate_soundtrack_plan(total_dur)
        
        self.assertEqual(plan.total_duration_sec, 1200.0)
        self.assertEqual(plan.total_segments, 4)
        
        # Verifica transições de mood
        moods = [s.mood for s in plan.segments]
        self.assertIn("suspense", moods)
        self.assertIn("investigative", moods)
        self.assertIn("dramatic_climax", moods)
        self.assertIn("inspiring", moods)

        # Verifica crossfade e ducking
        self.assertEqual(plan.segments[0].crossfade_duration_sec, 0.0) # Primeira faixa não tem crossfade
        self.assertGreater(plan.segments[1].crossfade_duration_sec, 0.0)
        self.assertEqual(plan.ducking_profile["speech_duck_db"], -22.0)
        self.assertEqual(plan.ducking_profile["pause_boost_db"], -6.0)

    def test_smart_ken_burns_and_punch_in(self):
        # 1. Imagem estática com Ken Burns
        kb_effect = SmartKenBurnsPunchInEngine.generate_effect(
            scene_order=1,
            duration_sec=6.0,
            is_still_image=True,
            is_key_emphasis=False
        )
        self.assertTrue(kb_effect.is_still_image)
        self.assertIn("zoompan=", kb_effect.ffmpeg_video_filter)
        self.assertIn(kb_effect.motion_type, SmartKenBurnsPunchInEngine.MOTION_PATTERNS)

        # 2. Momento de ênfase dramática (Punch-in 1.10x)
        punch_effect = SmartKenBurnsPunchInEngine.generate_effect(
            scene_order=2,
            duration_sec=4.0,
            is_still_image=False,
            is_key_emphasis=True
        )
        self.assertEqual(punch_effect.motion_type, "punch_in_emphasis")
        self.assertIn("crop=", punch_effect.ffmpeg_video_filter)
        self.assertEqual(punch_effect.start_scale, 1.10)

        # 3. Aplicação em lote
        batch_scenes = [
            {"order": 1, "duration": 5.0, "media_type": "image"},
            {"order": 2, "duration": 7.0, "media_type": "video", "is_key_point": True},
            {"order": 3, "duration": 4.0, "media_type": "video"}
        ]
        results = SmartKenBurnsPunchInEngine.apply_to_project_scenes(batch_scenes)
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].is_still_image)
        self.assertEqual(results[1].motion_type, "punch_in_emphasis")
        self.assertEqual(results[2].motion_type, "static_stabilized")

    def test_render_checkpoint_manager_crash_recovery(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            proj_id = "test_doc_20min"
            total_chunks = 10
            
            # Inicializa estado vazio
            state = RenderCheckpointManager.load_or_init_state(proj_id, total_chunks, tmp_dir)
            self.assertEqual(state.completed_chunks, 0)
            self.assertEqual(len(state.pending_chunks), 10)
            self.assertFalse(state.is_fully_completed)

            # Simula renderização de 4 chunks no disco
            for i in range(1, 5):
                fake_file = os.path.join(tmp_dir, f"chunk_{i:03d}.mp4")
                with open(fake_file, "wb") as f:
                    f.write(b"0" * 4096) # Arquivo válido > 1KB
                RenderCheckpointManager.record_chunk_completed(state, i, fake_file, 18.0)

            self.assertEqual(state.completed_chunks, 4)
            self.assertEqual(len(state.pending_chunks), 6)
            self.assertEqual(state.pending_chunks, [5, 6, 7, 8, 9, 10])

            # Simula queda e reabertura (Crash & Resume)
            resumed_state = RenderCheckpointManager.load_or_init_state(proj_id, total_chunks, tmp_dir)
            self.assertEqual(resumed_state.completed_chunks, 4)
            self.assertEqual(resumed_state.pending_chunks, [5, 6, 7, 8, 9, 10])

            # Completa os chunks restantes
            for i in range(5, 11):
                fake_file = os.path.join(tmp_dir, f"chunk_{i:03d}.mp4")
                with open(fake_file, "wb") as f:
                    f.write(b"0" * 4096)
                RenderCheckpointManager.record_chunk_completed(resumed_state, i, fake_file, 18.0)

            self.assertEqual(resumed_state.completed_chunks, 10)
            self.assertEqual(len(resumed_state.pending_chunks), 0)
            self.assertTrue(resumed_state.is_fully_completed)

            # Limpeza
            RenderCheckpointManager.cleanup_checkpoint(resumed_state)
            self.assertFalse(os.path.exists(resumed_state.checkpoint_file))

if __name__ == "__main__":
    unittest.main()
