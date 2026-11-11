import unittest
from core.numa_node_memory_locality_binder import NUMANodeMemoryLocalityBinder


class TestNUMANodeMemoryLocalityBinder(unittest.TestCase):
    def test_single_and_multi_node_topology(self):
        # Teste com 8 cores (1 nó)
        res8 = NUMANodeMemoryLocalityBinder.get_numa_binding_topology(target_threads=8)
        self.assertEqual(res8["status"], "success")
        self.assertEqual(res8["numa_nodes_count"], 1)

        # Teste com 16 cores (2 nós / multi-CCD)
        res16 = NUMANodeMemoryLocalityBinder.get_numa_binding_topology(target_threads=16)
        self.assertEqual(res16["numa_nodes_count"], 2)
        self.assertIn("numa_node_0", res16["node_assignments"])
        self.assertIn("numa_node_1", res16["node_assignments"])
        self.assertGreater(res16["cross_node_traffic_reduction_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
