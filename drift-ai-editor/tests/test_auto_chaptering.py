"""
Unit tests for AutoChapteringEngine in Drift AI.
Verifies timestamp calculations, YouTube description blocks, WebVTT, and FFmpeg metadata formats.
"""
import unittest
from pipeline.auto_chaptering import AutoChapteringEngine, VideoChapter
from models.scene_plan import ProjectPlan, Scene

class TestAutoChapteringEngine(unittest.TestCase):

    def test_format_timestamp(self):
        self.assertEqual(AutoChapteringEngine.format_timestamp(0.0), "00:00")
        self.assertEqual(AutoChapteringEngine.format_timestamp(65.0), "01:05")
        self.assertEqual(AutoChapteringEngine.format_timestamp(3670.0), "01:01:10")

    def test_generate_chapters_starts_at_zero(self):
        plan = ProjectPlan(title="História do Universo")
        plan.scenes = [
            Scene(order=1, narration_text="No princípio, a grande explosão deu origem a tudo.", duration=10.0),
            Scene(order=2, narration_text="As primeiras estrelas começaram a brilhar no vazio cósmico.", duration=15.0),
            Scene(order=3, narration_text="Galáxias espirais se formaram com bilhões de planetas.", duration=20.0)
        ]
        chapters = AutoChapteringEngine.generate_chapters(plan)
        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0].formatted_start, "00:00")
        self.assertEqual(chapters[1].formatted_start, "00:10")
        self.assertEqual(chapters[2].formatted_start, "00:25")

    def test_generate_youtube_description_block(self):
        plan = ProjectPlan(title="Guia de Produção")
        plan.scenes = [
            Scene(order=1, narration_text="Introdução ao método rápido de edição.", duration=12.0),
            Scene(order=2, narration_text="Configurando a timeline de alta performance.", duration=18.0)
        ]
        block = AutoChapteringEngine.generate_youtube_description_block(plan)
        self.assertIn("00:00", block)
        self.assertIn("00:12", block)
        self.assertIn("CAPÍTULOS", block)

    def test_generate_webvtt_and_ffmpeg_metadata(self):
        plan = ProjectPlan(title="Projeto Simples")
        plan.scenes = [
            Scene(order=1, narration_text="Cena 1 inicial.", duration=5.0)
        ]
        vtt = AutoChapteringEngine.generate_webvtt(plan)
        self.assertIn("WEBVTT", vtt)
        self.assertIn("00:00.000 --> 00:05.000", vtt)

        ffmpeg_meta = AutoChapteringEngine.generate_ffmpeg_metadata(plan)
        self.assertIn(";FFMETADATA1", ffmpeg_meta)
        self.assertIn("[CHAPTER]", ffmmeta := ffmpeg_meta)
        self.assertIn("START=0", ffmpeg_meta)
        self.assertIn("END=5000", ffmpeg_meta)

if __name__ == "__main__":
    unittest.main()
