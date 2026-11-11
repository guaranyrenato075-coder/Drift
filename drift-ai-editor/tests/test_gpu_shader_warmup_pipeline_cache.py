import unittest
from pipeline.gpu_shader_warmup_pipeline_cache import GPUShaderWarmupPipelineCache


class TestGPUShaderWarmupPipelineCache(unittest.TestCase):
    def test_warmup_shaders(self):
        res = GPUShaderWarmupPipelineCache.warmup_core_shaders(force_recompile=True)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_shaders_cached"], len(GPUShaderWarmupPipelineCache.CORE_SHADERS))
        self.assertGreater(res["stutter_reduction_pct"], 90.0)

        # Segundo warmup não deve recompilar nada (acerto de cache)
        res_cached = GPUShaderWarmupPipelineCache.warmup_core_shaders(force_recompile=False)
        self.assertEqual(res_cached["newly_compiled_in_warmup"], 0)


if __name__ == "__main__":
    unittest.main()
