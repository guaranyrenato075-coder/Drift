import unittest
from pipeline.gpu_pipeline_raster_early_z_culler import GPUPipelineRasterEarlyZCuller


class TestGPUPipelineRasterEarlyZCuller(unittest.TestCase):
    def test_cull_occluded_layers(self):
        layers = [
            {"id": "layer_0_bg", "rect": (0, 0, 1920, 1080), "opacity": 1.0},
            {"id": "layer_1_full_cover", "rect": (0, 0, 1920, 1080), "opacity": 1.0},
            {"id": "layer_2_overlay", "rect": (100, 100, 200, 200), "opacity": 0.5}
        ]
        res = GPUPipelineRasterEarlyZCuller.cull_occluded_layers(layers)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["culled_layers_count"], 1)
        self.assertIn("layer_0_bg", res["culled_layer_ids"])
        self.assertEqual(res["rendered_layers_count"], 2)

    def test_analyze_multitrack_overdraw_savings(self):
        res = GPUPipelineRasterEarlyZCuller.analyze_multitrack_overdraw_savings(total_layers=6)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["unnecessary_shaded_pixels_prevented"], 0)
        self.assertGreater(res["vram_bandwidth_saved_gbps"], 0.0)


if __name__ == "__main__":
    unittest.main()
