"""
Unit tests for CutWire Drift AI Eco-Optimization Suite:
1. EcoGovernor (Thread capping, priority management, thermal governors)
2. RamWorkingSetFlusher (Generational GC & Windows memory reclaim)
3. DraftProxyEngine (360p lightweight proxy generation & switching)
4. LosslessStreamCopyDetector (Zero-CPU stream copy detection)
"""
import unittest
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scene_plan import Scene, SceneState
from core.eco_governor import EcoGovernor, EcoPolicy
from core.ram_working_set_flusher import RamWorkingSetFlusher, RamFlushReport
from editing.draft_proxy_engine import DraftProxyEngine, DraftProxySession
from editing.lossless_stream_copy_detector import LosslessStreamCopyDetector, StreamCopyEvaluation

class TestEcoOptimizationSuite(unittest.TestCase):

    def test_eco_governor_budget(self):
        # Simula o processador Intel Xeon com 24 threads
        xeon_threads = 24
        
        # Modo Eco Silent: deve reservar 4 threads e limitar para 20 threads com prioridade BELOW_NORMAL
        eco = EcoGovernor.calculate_thread_budget("eco_silent", total_threads=xeon_threads)
        self.assertEqual(eco.total_system_threads, 24)
        self.assertEqual(eco.reserved_os_threads, 4)
        self.assertEqual(eco.assigned_worker_threads, 20)
        self.assertEqual(eco.windows_priority_class, "BELOW_NORMAL")
        self.assertEqual(eco.target_cpu_cap_percent, 80)

        # Modo Balanced: reserva 2 threads
        balanced = EcoGovernor.calculate_thread_budget("balanced", total_threads=xeon_threads)
        self.assertEqual(balanced.reserved_os_threads, 2)
        self.assertEqual(balanced.assigned_worker_threads, 22)

        # Modo Max Performance: usa todos os 24 threads
        max_p = EcoGovernor.calculate_thread_budget("maximum_performance", total_threads=xeon_threads)
        self.assertEqual(max_p.reserved_os_threads, 0)
        self.assertEqual(max_p.assigned_worker_threads, 24)

    def test_ram_working_set_flusher(self):
        # Aloca temporariamente algumas estruturas para testar descarte
        dummy_data = [list(range(5000)) for _ in range(20)]
        del dummy_data

        report = RamWorkingSetFlusher.flush()
        self.assertIsInstance(report, RamFlushReport)
        self.assertGreaterEqual(report.freed_python_objects, 0)
        self.assertGreaterEqual(report.working_set_before_mb, 0.0)

    def test_draft_proxy_engine(self):
        scenes = [
            Scene(order=1, duration=5.0, narration_text="Cena 1 com vídeo"),
            Scene(order=2, duration=4.0, narration_text="Cena 2 com imagem")
        ]
        
        session = DraftProxyEngine.build_session("proj_eco_01", scenes, proxies_dir="d:/CUTWIREDRIFT/renders/test_proxies")
        self.assertEqual(session.total_proxies, 2)
        self.assertTrue(session.is_draft_mode_active)

        # Verifica mapeamento da cena 1
        m1 = session.mappings[1]
        self.assertEqual(m1.scale_resolution, "640:360")
        cmd_str = " ".join(m1.ffmpeg_proxy_command)
        self.assertIn("scale=640:360", cmd_str)
        self.assertIn("-preset ultrafast", cmd_str)
        self.assertIn("-crf 28", cmd_str)

    def test_lossless_stream_copy_detector(self):
        # Caso 1: Vídeo H.264 1080p + Áudio AAC -> Cópia de fluxo direta (zero CPU)
        res_copy = LosslessStreamCopyDetector.evaluate_stream(
            media_path="clip_h264_1080p.mp4",
            target_width=1920,
            target_height=1080,
            has_effects_applied=False,
            codec_v="h264",
            codec_a="aac",
            width=1920,
            height=1080
        )
        self.assertTrue(res_copy.can_copy_video_stream)
        self.assertTrue(res_copy.can_copy_audio_stream)
        self.assertEqual(res_copy.recommended_video_codec, "copy")
        self.assertEqual(res_copy.recommended_audio_codec, "copy")
        self.assertGreaterEqual(res_copy.estimated_speedup_factor, 30.0)

        # Caso 2: Efeitos visuais ativos (Ken Burns, etc.) -> Deve re-encodar vídeo
        res_fx = LosslessStreamCopyDetector.evaluate_stream(
            media_path="clip_with_fx.mp4",
            has_effects_applied=True,
            codec_v="h264",
            codec_a="aac"
        )
        self.assertFalse(res_fx.can_copy_video_stream)
        self.assertEqual(res_fx.recommended_video_codec, "libx264")

        # Caso 3: Resolução incompatível (ex: 720p para 1080p) -> Deve re-encodar vídeo
        res_scale = LosslessStreamCopyDetector.evaluate_stream(
            media_path="clip_720p.mp4",
            target_width=1920,
            target_height=1080,
            width=1280,
            height=720
        )
        self.assertFalse(res_scale.can_copy_video_stream)
        self.assertEqual(res_scale.recommended_video_codec, "libx264")

if __name__ == "__main__":
    unittest.main()
