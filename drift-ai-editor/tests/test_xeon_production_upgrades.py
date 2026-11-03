import unittest
import os
from pathlib import Path
from models.scene_plan import ProjectPlan, ProjectConfig, Scene
from core.hardware_telemetry import HardwareTelemetryProfiler, HardwareTelemetryReport
from pipeline.chunked_parallel_renderer import ChunkedParallelRenderer, ParallelRenderPlan
from editing.karaoke_subtitle_generator import KaraokeSubtitleGenerator, KaraokeSubtitleScript
from voice.local_neural_fallback import LocalNeuralVoiceFallback, LocalTtsSynthesisResult

class TestXeonProductionUpgrades(unittest.TestCase):

    def setUp(self):
        self.plan = ProjectPlan(
            project_id="xeon_test_project",
            title="O Domínio da Produtividade",
            config=ProjectConfig(aspect_ratio="16:9", media_type="video"),
            scenes=[
                Scene(
                    order=1,
                    narration_text="O segredo do sucesso nunca foi a sorte.",
                    duration=4.5
                ),
                Scene(
                    order=2,
                    narration_text="Atenção plena e foco transformam qualquer objetivo em realidade.",
                    duration=6.0
                ),
                Scene(
                    order=3,
                    narration_text="Controle sua mente antes que o mundo controle você.",
                    duration=5.0
                ),
                Scene(
                    order=4,
                    narration_text="Comece hoje mesmo com determinação inabalável.",
                    duration=4.0
                )
            ]
        )

    def test_hardware_telemetry_profiler(self):
        report = HardwareTelemetryProfiler.get_telemetry()
        self.assertIsInstance(report, HardwareTelemetryReport)
        self.assertGreaterEqual(report.total_threads, 4)
        self.assertGreaterEqual(report.ram_total_gb, 8.0)
        self.assertGreaterEqual(report.ram_free_gb, 1.0)
        self.assertIsNotNone(report.active_encoder_mode)
        self.assertIn(report.health_status, ["EXCELLENT", "NORMAL", "THROTTLED"])
        self.assertGreaterEqual(report.recommended_concurrency, 2)

    def test_chunked_parallel_renderer(self):
        plan = ChunkedParallelRenderer.create_parallel_plan(
            self.plan,
            target_chunk_sec=10.0,
            output_dir="d:/CUTWIREDRIFT/test_renders"
        )
        self.assertIsInstance(plan, ParallelRenderPlan)
        self.assertEqual(plan.total_scenes, 4)
        self.assertGreaterEqual(plan.total_chunks, 1)
        self.assertGreaterEqual(plan.concurrency_slots, 2)
        self.assertGreaterEqual(plan.estimated_speedup_factor, 1.5)
        self.assertIn("file '", plan.ffmpeg_concat_manifest)

        # Checagem dos chunks individuais
        first_chunk = plan.chunks[0]
        self.assertGreater(len(first_chunk.encoder_args), 0)
        self.assertGreater(first_chunk.assigned_thread_budget, 0)
        self.assertTrue(first_chunk.output_temp_file.endswith(".mp4"))

    def test_karaoke_subtitle_generator(self):
        karaoke_script = KaraokeSubtitleGenerator.generate_ass_script(
            self.plan,
            font_name="Montserrat ExtraBold",
            font_size=60,
            highlight_color_hex="#00FF66",
            safe_zone_vertical_margin=420
        )
        self.assertIsInstance(karaoke_script, KaraokeSubtitleScript)
        self.assertEqual(karaoke_script.total_lines, 4)
        self.assertIn("[Script Info]", karaoke_script.ass_script_content)
        self.assertIn("Style: HormoziKaraoke", karaoke_script.ass_script_content)
        self.assertIn("Dialogue: 0,", karaoke_script.ass_script_content)
        # Deve conter tags \k de karaoke
        self.assertIn(r"{\k", karaoke_script.ass_script_content)

    def test_local_neural_voice_fallback(self):
        test_wav = "d:/CUTWIREDRIFT/test_audio/test_xeon_voice.wav"
        try:
            res = LocalNeuralVoiceFallback.synthesize_speech(
                text="Este é um teste do motor neural offline otimizado para CPU.",
                output_wav_path=test_wav,
                profile_id="pt_br_documentary_deep"
            )
            self.assertIsInstance(res, LocalTtsSynthesisResult)
            self.assertTrue(os.path.exists(res.audio_path))
            self.assertGreater(res.duration_sec, 1.0)
            self.assertEqual(res.sample_rate, 24000)
            self.assertGreater(os.path.getsize(res.audio_path), 1000)
        finally:
            if os.path.exists(test_wav):
                try:
                    os.remove(test_wav)
                except Exception:
                    pass

if __name__ == "__main__":
    unittest.main()

