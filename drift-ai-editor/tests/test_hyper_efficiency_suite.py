"""
Unit tests for CutWire Drift AI Hyper Efficiency Suite:
1. LazyTimelineVirtualizer (Playhead sliding window handle virtualization)
2. FlacInMemoryScratchpad (Lossless audio compression in memory)
3. ZeroFragmentationPreallocator (Contiguous disk cluster preallocation)
4. GreenWattageCapper (Core affinity clustering and wattage capping)
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scene_plan import Scene, SceneState
from editing.lazy_timeline_virtualizer import LazyTimelineVirtualizer, VirtualizerWindowState
from audio.flac_in_memory_scratchpad import FlacInMemoryScratchpad, AudioBufferStats
from storage.zero_fragmentation_preallocator import ZeroFragmentationPreallocator, PreallocationResult
from core.green_wattage_capper import GreenWattageCapper, PowerSavingProfile

class TestHyperEfficiencySuite(unittest.TestCase):

    def test_lazy_timeline_virtualizer(self):
        # Cria 50 cenas simuladas
        scenes = [Scene(order=i, duration=5.0) for i in range(1, 51)]

        virtualizer = LazyTimelineVirtualizer(window_radius=2)
        virtualizer.register_scenes(scenes)

        # Posiciona playhead na cena 10 (janela de 8 a 12 = 5 cenas ativas)
        w_state = virtualizer.update_playhead(10)
        self.assertEqual(w_state.total_scenes, 50)
        self.assertEqual(w_state.active_handles_count, 5)
        self.assertEqual(w_state.hibernating_handles_count, 45)

        # Verifica alocação dos handles
        self.assertTrue(w_state.handles[10].is_active)
        self.assertTrue(w_state.handles[8].is_active)
        self.assertTrue(w_state.handles[12].is_active)
        self.assertFalse(w_state.handles[1].is_active)
        self.assertTrue(w_state.handles[1].is_hibernating)

        # Move playhead para a cena 1 (borda: cenas 1, 2, 3 ativas = 3 ativas)
        w_state2 = virtualizer.update_playhead(1)
        self.assertEqual(w_state2.active_handles_count, 3)
        self.assertEqual(w_state2.hibernating_handles_count, 47)

    def test_flac_in_memory_scratchpad(self):
        scratchpad = FlacInMemoryScratchpad()

        # Cria 10 segundos de áudio estéreo 48kHz (48000 * 2 canais * 2 bytes = 192.000 bytes)
        raw_pcm = b"\x00\x01\x00\x02" * 48000

        stats = scratchpad.store_pcm_track("voice_narration", raw_pcm, sample_rate=48000, channels=2)
        self.assertEqual(stats.raw_pcm_bytes, 192000)
        self.assertLess(stats.compressed_bytes, stats.raw_pcm_bytes)
        self.assertGreater(stats.savings_percent, 50.0)

        # Recuperação perfeita sem perdas (lossless)
        retrieved = scratchpad.retrieve_pcm_track("voice_narration")
        self.assertEqual(retrieved, raw_pcm)

    def test_zero_fragmentation_preallocator(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_file = os.path.join(tmp_dir, "test_render.mp4")
            # Estima tamanho para 60 segundos de vídeo a 8 Mbps
            size_est = ZeroFragmentationPreallocator.estimate_video_file_size_bytes(60.0, bitrate_mbps=8.0)
            self.assertGreater(size_est, 1024 * 1024)

            # Executa pré-alocação no disco
            res = ZeroFragmentationPreallocator.preallocate_file(target_file, size_est)
            self.assertTrue(res.is_success)
            self.assertEqual(res.preallocated_bytes, size_est)
            self.assertTrue(os.path.exists(target_file))
            self.assertEqual(os.path.getsize(target_file), size_est)

    def test_green_wattage_capper(self):
        # Xeon com 24 threads
        xeon_cores = 24

        # Perfil Ultra Green (50% dos núcleos primários)
        p_green = GreenWattageCapper.calculate_power_profile("ultra_green", total_logical_cores=xeon_cores)
        self.assertEqual(p_green.active_core_count, 12)
        self.assertEqual(p_green.estimated_wattage_reduction_pct, 35)
        self.assertEqual(p_green.estimated_tdp_watts, 68)

        # Perfil Balanced (75% dos núcleos)
        p_bal = GreenWattageCapper.calculate_power_profile("balanced_power", total_logical_cores=xeon_cores)
        self.assertEqual(p_bal.active_core_count, 18)
        self.assertEqual(p_bal.estimated_wattage_reduction_pct, 20)

        # Perfil Full TDP
        p_full = GreenWattageCapper.calculate_power_profile("full_tdp", total_logical_cores=xeon_cores)
        self.assertEqual(p_full.active_core_count, 24)
        self.assertEqual(p_full.estimated_wattage_reduction_pct, 0)

if __name__ == "__main__":
    unittest.main()
