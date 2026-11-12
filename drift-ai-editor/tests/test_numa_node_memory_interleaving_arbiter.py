import unittest
from core.numa_node_memory_interleaving_arbiter import NUMANodeMemoryInterleavingArbiter


class TestNUMANodeMemoryInterleavingArbiter(unittest.TestCase):
    def test_detect_numa_topology(self):
        topo = NUMANodeMemoryInterleavingArbiter.detect_numa_topology()
        self.assertEqual(topo["status"], "success")
        self.assertGreaterEqual(topo["detected_numa_nodes"], 1)
        self.assertGreaterEqual(topo["logical_cpus"], 1)
        self.assertIn("summary", topo)

    def test_plan_thread_buffer_affinity(self):
        aff0 = NUMANodeMemoryInterleavingArbiter.plan_thread_buffer_affinity(thread_id=0, total_nodes=2)
        aff1 = NUMANodeMemoryInterleavingArbiter.plan_thread_buffer_affinity(thread_id=1, total_nodes=2)
        self.assertEqual(aff0["assigned_numa_node"], 0)
        self.assertEqual(aff1["assigned_numa_node"], 1)
        self.assertGreater(aff0["memory_bandwidth_efficiency_pct"], 90.0)


if __name__ == "__main__":
    unittest.main()
