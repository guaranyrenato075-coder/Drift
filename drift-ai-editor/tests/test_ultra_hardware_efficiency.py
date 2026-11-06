"""
Unit tests for CutWire Drift AI Ultra Hardware Efficiency Suite:
1. ThermalDutyCyclePacer (Cadence-based micro cooling pauses)
2. ZeroGpuOcclusionGovernor (Window minimization & GUI framerate throttle)
3. CompactMetadataIndexer (Zlib byte-packed scene indexing)
4. DirectClockAudioResampler (48kHz libsoxr ingest resampler)
"""
import unittest
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scene_plan import Scene, SceneState
from core.thermal_duty_cycle import ThermalDutyCyclePacer, ThermalPacingDecision
from core.zero_gpu_occlusion_governor import ZeroGpuOcclusionGovernor, WindowOcclusionState
from core.compact_metadata_indexer import CompactMetadataIndexer, CompactIndexStats
from audio.direct_clock_resampler import DirectClockAudioResampler, AudioResampleSpec

class TestUltraHardwareEfficiency(unittest.TestCase):

    def test_thermal_duty_cycle_pacer(self):
        pacer = ThermalDutyCyclePacer(chunks_per_cooling_cycle=3, pause_duration_sec=1.5)

        # Chunks 1 e 2: dentro da janela segura
        d1 = pacer.record_chunk_completed(1)
        self.assertFalse(d1.should_pause_for_cooling)
        self.assertEqual(d1.cooling_pause_sec, 0.0)

        d2 = pacer.record_chunk_completed(2)
        self.assertFalse(d2.should_pause_for_cooling)

        # Chunk 3: ciclo atingido, deve pausar para resfriamento
        d3 = pacer.record_chunk_completed(3)
        self.assertTrue(d3.should_pause_for_cooling)
        self.assertEqual(d3.cooling_pause_sec, 1.5)
        self.assertGreater(d3.estimated_temp_drop_celsius, 3.0)
        self.assertEqual(pacer.total_pauses_inserted, 1)

        # Chunk 4: ciclo reiniciado
        d4 = pacer.record_chunk_completed(4)
        self.assertFalse(d4.should_pause_for_cooling)

    def test_zero_gpu_occlusion_governor(self):
        # 1. Modo em foco: 60 FPS
        ZeroGpuOcclusionGovernor.set_simulation_state(is_minimized=False, is_foreground=True)
        st_fg = ZeroGpuOcclusionGovernor.get_occlusion_state()
        self.assertFalse(st_fg.is_minimized)
        self.assertTrue(st_fg.is_foreground)
        self.assertEqual(st_fg.target_gui_fps, 60)
        self.assertTrue(st_fg.gpu_render_active)

        # 2. Modo segundo plano: 15 FPS
        ZeroGpuOcclusionGovernor.set_simulation_state(is_minimized=False, is_foreground=False)
        st_bg = ZeroGpuOcclusionGovernor.get_occlusion_state()
        self.assertEqual(st_bg.target_gui_fps, 15)

        # 3. Modo minimizado: 1 FPS (GPU em repouso)
        ZeroGpuOcclusionGovernor.set_simulation_state(is_minimized=True, is_foreground=False)
        st_min = ZeroGpuOcclusionGovernor.get_occlusion_state()
        self.assertTrue(st_min.is_minimized)
        self.assertEqual(st_min.target_gui_fps, 1)
        self.assertFalse(st_min.gpu_render_active)

    def test_compact_metadata_indexer(self):
        scenes = []
        for i in range(1, 101):
            sc = Scene(
                order=i,
                narration_text=f"Narração longa com detalhes históricos da cena {i} para testar a taxa de compressão de metadados em memória.",
                duration=6.0
            )
            scenes.append(sc)

        indexer = CompactMetadataIndexer()
        stats = indexer.index_scenes(scenes)

        self.assertEqual(stats.total_scenes_indexed, 100)
        self.assertGreater(stats.raw_json_bytes, stats.compressed_bytes)
        self.assertGreaterEqual(stats.compression_ratio, 2.0)
        self.assertGreaterEqual(stats.memory_savings_percent, 50.0)

        # Recuperação íntegra
        retrieved = indexer.retrieve_scene(42)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.get("order"), 42)
        self.assertIn("cena 42", retrieved.get("narration_text"))

    def test_direct_clock_audio_resampler(self):
        spec = DirectClockAudioResampler.build_resample_spec("raw_audio_22k.mp3")
        self.assertEqual(spec.target_sample_rate_hz, 48000)
        self.assertEqual(spec.target_channels, 2)
        self.assertEqual(spec.resampler_engine, "soxr")

        cmd = " ".join(spec.ffmpeg_filter_args)
        self.assertIn("aresample=resampler=soxr:osr=48000", cmd)
        self.assertIn("stereo", cmd)
        self.assertIn("-c:a libmp3lame", cmd)

if __name__ == "__main__":
    unittest.main()
