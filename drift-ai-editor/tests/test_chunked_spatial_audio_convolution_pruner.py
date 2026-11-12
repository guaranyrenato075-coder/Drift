import unittest
from audio.chunked_spatial_audio_convolution_pruner import ChunkedSpatialAudioConvolutionPruner


class TestChunkedSpatialAudioConvolutionPruner(unittest.TestCase):
    def test_prune_impulse_response(self):
        res = ChunkedSpatialAudioConvolutionPruner.prune_impulse_response()
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["pruned_tail_samples"], 0)
        self.assertGreater(res["retained_active_samples"], 0)
        self.assertTrue(res["psychoacoustic_transparency"])

    def test_analyze_cpu_convolution_relief(self):
        analysis = ChunkedSpatialAudioConvolutionPruner.analyze_cpu_convolution_relief()
        self.assertEqual(analysis["status"], "success")
        self.assertGreater(analysis["cpu_convolution_load_reduction_pct"], 80.0)


if __name__ == "__main__":
    unittest.main()
