import unittest
from pipeline.vram_paged_pool_fragmentation_defrag import VRAMPagedPoolFragmentationDefrag


class TestVRAMPagedPoolFragmentationDefrag(unittest.TestCase):
    def test_slab_efficiency_analysis(self):
        res = VRAMPagedPoolFragmentationDefrag.analyze_vram_slab_efficiency(
            allocated_textures_count=30,
            total_vram_used_mb=1200.0,
            unaligned_allocations_count=10
        )
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["vram_fragmentation_prevented_mb"], 0.0)
        self.assertGreater(res["fragmentation_reduction_pct"], 70.0)
        self.assertGreater(res["pcie_ram_spills_prevented"], 0)


if __name__ == "__main__":
    unittest.main()
