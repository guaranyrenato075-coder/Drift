import unittest
from media.smart_av_sync_drift_compensator import SmartAVSyncDriftCompensator


class TestSmartAVSyncDriftCompensator(unittest.TestCase):
    def test_perfect_lock_and_drift_correcting(self):
        # Desvio zero
        lock = SmartAVSyncDriftCompensator.calculate_sync_alignment(audio_clock_sec=100.0, video_pts_sec=100.002)
        self.assertEqual(lock["status"], "success")
        self.assertEqual(lock["sync_state"], "PERFECT_LOCK")

        # Desvio acentuado (>40ms)
        drift = SmartAVSyncDriftCompensator.calculate_sync_alignment(audio_clock_sec=100.0, video_pts_sec=100.065)
        self.assertEqual(drift["sync_state"], "DRIFT_CORRECTING")
        self.assertTrue(drift["resample_avoided"])


if __name__ == "__main__":
    unittest.main()
