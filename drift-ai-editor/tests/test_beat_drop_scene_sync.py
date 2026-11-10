"""
Unit tests for SoundtrackBeatDropSceneSync in CutWire Drift AI.
Verifies BPM calculation, scene duration quantization to musical bars, and timeline sync.
"""
import unittest
from audio.beat_drop_scene_sync import SoundtrackBeatDropSceneSync
from models.scene_plan import ProjectPlan, Scene

class TestBeatDropSceneSync(unittest.TestCase):

    def test_calculate_beat_interval(self):
        # 120 BPM = 0.5 sec per beat
        self.assertEqual(SoundtrackBeatDropSceneSync.calculate_beat_interval(120.0), 0.5)
        # 60 BPM = 1.0 sec per beat
        self.assertEqual(SoundtrackBeatDropSceneSync.calculate_beat_interval(60.0), 1.0)

    def test_quantize_scene_cut(self):
        # At 120 BPM, half-bar is 1.0s, bar is 2.0s
        dur, shift, bars = SoundtrackBeatDropSceneSync.quantize_scene_cut(3.4, 120.0)
        # 3.4 is closest to 3.0s (3 half-bars)
        self.assertAlmostEqual(dur, 3.0, places=2)
        self.assertAlmostEqual(shift, -400.0, places=1)
        self.assertEqual(bars, 2)

    def test_synchronize_timeline_to_bpm(self):
        plan = ProjectPlan(title="Projeto Rítmico")
        plan.scenes = [
            Scene(order=1, duration=3.2),
            Scene(order=2, duration=4.6),
            Scene(order=3, duration=2.1)
        ]

        res = SoundtrackBeatDropSceneSync.synchronize_timeline_to_bpm(plan, bpm=90.0)
        self.assertEqual(res["total_cuts_quantized"], 3)
        self.assertEqual(res["tempo_bpm"], 90.0)
        self.assertGreater(res["total_synchronized_duration_sec"], 0)

if __name__ == '__main__':
    unittest.main()
