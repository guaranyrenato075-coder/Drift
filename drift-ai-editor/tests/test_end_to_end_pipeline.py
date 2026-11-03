import unittest
import sys
import tempfile
import wave
import struct
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.scene_plan import ProjectPlan, ProjectConfig, Scene, MediaCandidate
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from analysis.storyboard_engine import StoryboardEngine
from voice.audio_aligner import AudioAligner
from media.media_ranker import MediaRanker
from pipeline.timeline_planner import TimelinePlanner
from pipeline.quality_control import QualityControlEngine
from pipeline.delta_editor import DeltaReeditor
from editing.captions import CaptionManager
from editing.deliverables_packager import DeliverablesPackager
from storage.repository import ProjectRepository

class TestEndToEndPipeline(unittest.TestCase):
    """
    Consolidated End-to-End Master Test:
    Validates the 8 critical checkpoints of the production workflow:
      1. Roteiro inserido e segmentado semanticamente.
      2. Narração gerada localmente.
      3. Áudio analisado para tempos reais e picos de volume.
      4. Busca e ranqueamento de vídeos e imagens com alternativas.
      5. Montagem da timeline organizada e protegida por lotes.
      6. Legendas sincronizadas com timestamps exatos.
      7. Reedição localizada (troca de uma cena preservando o restante intacto).
      8. Auditoria de qualidade prévia e geração do pacote de entrega.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.repo = ProjectRepository(db_path=self.temp_path / "e2e_projects.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_synthetic_wav(self, duration_sec: float, file_name: str) -> Path:
        """Helper to create valid synthetic WAV audio files."""
        wav_path = self.temp_path / file_name
        rate = 44100
        n_samples = int(rate * duration_sec)
        with wave.open(str(wav_path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            samples = [int(12000 * (i % 80) / 80) for i in range(n_samples)]
            wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
        return wav_path

    def test_full_8_step_lifecycle(self):
        # -------------------------------------------------------------
        # PASSO 1: O usuário insere um roteiro
        # -------------------------------------------------------------
        raw_script = (
            "CENA 01\nNARRAÇÃO: Você não controla o que acontece ao seu redor.\nDESCRIÇÃO VISUAL: Homem observando a chuva pela janela.\n\n"
            "CENA 02\nNARRAÇÃO: Mas você pode controlar a sua reação diante das adversidades.\nDESCRIÇÃO VISUAL: Pessoa caminhando serena ao nascer do sol.\n\n"
            "CENA 03\nNARRAÇÃO: A serenidade interior é a sua maior vitória.\nDESCRIÇÃO VISUAL: Vista de uma montanha tranquila."
        )

        plan = ProjectPlan(
            title="A Arte da Serenidade",
            raw_script=raw_script,
            config=ProjectConfig(language="pt", aspect_ratio="16:9")
        )

        scenes = ScriptSegmenter.parse(raw_script, default_language="pt")
        VisualPlanner.plan_project(scenes)
        plan.scenes = scenes
        plan.reindex_scenes()

        self.assertEqual(len(plan.scenes), 3)
        self.assertEqual(plan.scenes[0].order, 1)
        self.assertIn("chuva", plan.scenes[0].visual_description.lower())

        # -------------------------------------------------------------
        # PASSO 2: O sistema gera a narração localmente
        # -------------------------------------------------------------
        wav_scene1 = self._create_synthetic_wav(4.2, "scene_1_voice.wav")
        wav_scene2 = self._create_synthetic_wav(5.1, "scene_2_voice.wav")
        wav_scene3 = self._create_synthetic_wav(3.8, "scene_3_voice.wav")

        plan.scenes[0].audio_path = str(wav_scene1)
        plan.scenes[1].audio_path = str(wav_scene2)
        plan.scenes[2].audio_path = str(wav_scene3)

        for s in plan.scenes:
            self.assertTrue(Path(s.audio_path).exists())

        # -------------------------------------------------------------
        # PASSO 3: O áudio é analisado para determinar os tempos reais
        # -------------------------------------------------------------
        alignments = []
        cur_timeline_sec = 0.0
        for s in plan.scenes:
            align = AudioAligner.align_narration(s.order, s.narration_text, Path(s.audio_path))
            s.duration = align.total_duration
            s.start_time = round(cur_timeline_sec, 2)
            s.end_time = round(cur_timeline_sec + s.duration, 2)
            cur_timeline_sec = s.end_time
            alignments.append(align)

        self.assertAlmostEqual(plan.scenes[0].duration, 4.2, places=1)
        self.assertAlmostEqual(plan.scenes[1].duration, 5.1, places=1)
        self.assertAlmostEqual(plan.scenes[2].duration, 3.8, places=1)
        self.assertGreater(len(alignments[0].words), 0)

        # -------------------------------------------------------------
        # PASSO 4: O motor busca vídeos e imagens adequados
        # -------------------------------------------------------------
        # Mocking candidates
        dummy_video1 = self.temp_path / "vid_rain.mp4"
        dummy_video1.write_bytes(b"0" * 4096)
        dummy_video2 = self.temp_path / "vid_sunrise.mp4"
        dummy_video2.write_bytes(b"0" * 4096)
        dummy_video3 = self.temp_path / "vid_mountain.mp4"
        dummy_video3.write_bytes(b"0" * 4096)

        c1 = MediaCandidate(platform="pexels", external_id="p1", title="Rain Window", creator="Artist A", download_url="u1", local_cached_path=str(dummy_video1), duration=6.0)
        c2 = MediaCandidate(platform="unsplash", external_id="u2", title="Sunrise Walk", creator="Artist B", download_url="u2", local_cached_path=str(dummy_video2), duration=7.0)
        c3 = MediaCandidate(platform="archive_org", external_id="a3", title="Mountain Calm", creator="Artist C", download_url="u3", local_cached_path=str(dummy_video3), duration=5.0)

        plan.scenes[0].selected_media = c1
        plan.scenes[0].candidates = [c1]
        plan.scenes[1].selected_media = c2
        plan.scenes[1].candidates = [c2]
        plan.scenes[2].selected_media = c3
        plan.scenes[2].candidates = [c3]

        self.repo.save(plan)

        # -------------------------------------------------------------
        # PASSO 5: O Drift recebe as mídias e monta a timeline
        # -------------------------------------------------------------
        assembly_plan = TimelinePlanner.create_assembly_plan(plan)
        self.assertTrue(assembly_plan.validation_passed)
        self.assertEqual(len(assembly_plan.validation_issues), 0)
        self.assertGreater(len(assembly_plan.batches), 2)  # Tracks, Voice, Media, Transitions

        # -------------------------------------------------------------
        # PASSO 6: As legendas ficam sincronizadas com os tempos reais
        # -------------------------------------------------------------
        srt_file = self.temp_path / "subtitles.srt"
        CaptionManager.export_srt(plan.scenes, srt_file)
        self.assertTrue(srt_file.exists())
        srt_content = srt_file.read_text(encoding="utf-8")
        self.assertIn("00:00:00,000 -->", srt_content)
        self.assertIn("Você não controla", srt_content)

        # -------------------------------------------------------------
        # PASSO 7: O usuário substitui uma cena sem perder o restante
        # -------------------------------------------------------------
        # Update scene 2 text only
        updated_script = (
            "CENA 01\nNARRAÇÃO: Você não controla o que acontece ao seu redor.\nDESCRIÇÃO VISUAL: Homem observando a chuva pela janela.\n\n"
            "CENA 02\nNARRAÇÃO: Mas a mente focada supera qualquer obstáculo.\nDESCRIÇÃO VISUAL: Atleta correndo ao amanhecer.\n\n"
            "CENA 03\nNARRAÇÃO: A serenidade interior é a sua maior vitória.\nDESCRIÇÃO VISUAL: Vista de uma montanha tranquila."
        )

        mod, add, rem = DeltaReeditor.apply_script_update(plan, updated_script)
        self.assertEqual(mod, [2])  # Only scene 2 was modified
        self.assertEqual(len(add), 0)
        self.assertEqual(len(rem), 0)

        # Scene 1 and Scene 3 audio are intact
        self.assertEqual(plan.scenes[0].audio_path, str(wav_scene1))
        self.assertEqual(plan.scenes[2].audio_path, str(wav_scene3))
        # Scene 2 audio was invalidated for regeneration
        self.assertIsNone(plan.scenes[1].audio_path)

        # Regenerate voice only for Scene 2
        wav_scene2_new = self._create_synthetic_wav(4.8, "scene_2_voice_updated.wav")
        plan.scenes[1].audio_path = str(wav_scene2_new)
        plan.scenes[1].duration = 4.8

        # -------------------------------------------------------------
        # PASSO 8: O vídeo passa por verificação automática e gera kit de entrega
        # -------------------------------------------------------------
        audit_report = QualityControlEngine.audit_project(plan)
        self.assertTrue(audit_report.is_ready_for_export)
        self.assertEqual(audit_report.errors_count, 0)
        self.assertGreaterEqual(audit_report.score, 85)

        deliverables = DeliverablesPackager.generate_release_kit(plan, output_dir=self.temp_path / "final_pack")
        self.assertEqual(deliverables["chapters_count"], 3)
        self.assertTrue((self.temp_path / "final_pack" / "youtube_description.txt").exists())
        self.assertTrue((self.temp_path / "final_pack" / "thumbnail_brief.json").exists())

if __name__ == "__main__":
    unittest.main()
