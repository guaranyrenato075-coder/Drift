"""
Unit tests for AdaptiveHardwareGPUAutoTuner in CutWire Drift AI.
Verifies hardware detection, CPU/GPU profile generation, and FFmpeg command compilation.
"""
import unittest
from core.hardware_gpu_tuner import AdaptiveHardwareGPUAutoTuner

class TestHardwareGPUTuner(unittest.TestCase):

    def test_probe_hardware(self):
        prof = AdaptiveHardwareGPUAutoTuner.probe_hardware()

        self.assertIsNotNone(prof.platform_system)
        self.assertIn(prof.detected_gpu, ["nvidia", "intel_qsv", "amd_amf", "cpu_multicore"])
        self.assertIn(prof.recommended_encoder, ["h264_nvenc", "libx264", "h264_qsv", "h264_amf"])
        self.assertGreater(prof.cpu_thread_allocation, 0)
        self.assertIn("-c:v", prof.ffmpeg_video_flags)

    def test_get_render_command(self):
        cmd = AdaptiveHardwareGPUAutoTuner.get_render_command("input.mp4", "output.mp4")
        self.assertIn("ffmpeg -y -i input.mp4", cmd)
        self.assertIn("output.mp4", cmd)
        self.assertIn("-c:a aac", cmd)

if __name__ == '__main__':
    unittest.main()
