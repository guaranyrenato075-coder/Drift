"""
Unit tests for CutWire Drift AI Low-Level Hardware Optimization Suite:
1. DiskIoGovernor (Windows PROCESS_MODE_BACKGROUND_BEGIN)
2. FastDecodeOptimizer (Low-overhead decoding with -tune fastdecode)
3. SleepInhibitGovernor (Power management & execution state locks)
4. RollingCachePurgeManager (FIFO disk cache quota enforcement)
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.disk_io_governor import DiskIoGovernor, DiskIoStatus
from editing.fast_decode_optimizer import FastDecodeOptimizer, FastDecodeProfile
from core.sleep_inhibit_governor import SleepInhibitGovernor, SleepInhibitState
from storage.rolling_cache_purge import RollingCachePurgeManager, CachePurgeReport

class TestLowLevelOptimizations(unittest.TestCase):

    def test_disk_io_governor(self):
        # Inicia I/O em segundo plano
        status_begin = DiskIoGovernor.begin_background_io()
        self.assertIsInstance(status_begin, DiskIoStatus)
        
        # Encerra I/O em segundo plano
        status_end = DiskIoGovernor.end_background_io()
        self.assertIsInstance(status_end, DiskIoStatus)
        self.assertFalse(DiskIoGovernor.is_active())

    def test_fast_decode_optimizer(self):
        # Modo Preview (alta economia)
        preview_prof = FastDecodeOptimizer.get_trim_and_slice_args(threads=2, is_preview_mode=True)
        self.assertEqual(preview_prof.skip_frames, "noref")
        self.assertEqual(preview_prof.tune_mode, "fastdecode")
        self.assertGreaterEqual(preview_prof.estimated_cpu_saving_percent, 30)
        self.assertIn("-tune", preview_prof.ffmpeg_output_args)
        self.assertIn("fastdecode", preview_prof.ffmpeg_output_args)

        # Modo Normal (export)
        export_prof = FastDecodeOptimizer.get_trim_and_slice_args(threads=4, is_preview_mode=False)
        self.assertEqual(export_prof.skip_frames, "default")
        self.assertEqual(export_prof.thread_count, 4)

        # Construção do comando otimizado
        cmd = FastDecodeOptimizer.build_optimized_trim_command("in.mp4", 10.0, 5.0, "out.mp4", is_preview=True)
        self.assertIn("-ss", cmd)
        self.assertIn("-tune", cmd)
        self.assertIn("fastdecode", cmd)

    def test_sleep_inhibit_governor(self):
        # Inibe descanso do Windows
        state1 = SleepInhibitGovernor.inhibit_sleep()
        self.assertTrue(state1.is_sleep_inhibited)
        self.assertEqual(state1.active_jobs_count, 1)
        self.assertTrue(SleepInhibitGovernor.is_inhibited())

        # Simula segundo job simultâneo
        state2 = SleepInhibitGovernor.inhibit_sleep()
        self.assertEqual(state2.active_jobs_count, 2)

        # Libera job 1
        state3 = SleepInhibitGovernor.release_sleep()
        self.assertTrue(state3.is_sleep_inhibited)
        self.assertEqual(state3.active_jobs_count, 1)

        # Libera job 2 (restaura descanso do SO)
        state4 = SleepInhibitGovernor.release_sleep()
        self.assertFalse(state4.is_sleep_inhibited)
        self.assertEqual(state4.active_jobs_count, 0)
        self.assertFalse(SleepInhibitGovernor.is_inhibited())

    def test_rolling_cache_purge_manager(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Cria 5 arquivos de 100 KB cada = ~500 KB total
            files = []
            for i in range(1, 6):
                fp = os.path.join(tmp_dir, f"chunk_{i:03d}.tmp")
                with open(fp, "wb") as f:
                    f.write(b"X" * 102400)
                files.append(fp)

            # Cota estrita de 250 KB (deve deletar os 3 arquivos mais antigos para caber)
            report = RollingCachePurgeManager.enforce_cache_quota(tmp_dir, max_bytes_quota=250 * 1024)
            self.assertEqual(report.total_files_before, 5)
            self.assertGreaterEqual(report.files_deleted, 2)
            self.assertTrue(report.is_quota_respected)
            self.assertLessEqual(report.total_bytes_after, 250 * 1024)

if __name__ == "__main__":
    unittest.main()
