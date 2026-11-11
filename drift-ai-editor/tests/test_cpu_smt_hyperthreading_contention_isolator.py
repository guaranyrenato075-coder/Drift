import unittest
from core.cpu_smt_hyperthreading_contention_isolator import CPUSMTHyperthreadingContentionIsolator


class TestCPUSMTHyperthreadingContentionIsolator(unittest.TestCase):
    def test_smt_mapping(self):
        # Teste com 8 núcleos lógicos (4 físicos)
        res = CPUSMTHyperthreadingContentionIsolator.get_smt_topology_mapping(total_logical_cores=8)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["detected_logical_cores"], 8)
        self.assertEqual(res["estimated_physical_cores"], 4)
        self.assertEqual(len(res["isolated_heavy_threads"]), 4)
        self.assertGreater(res["ipc_efficiency_gain_pct"], 20.0)


if __name__ == "__main__":
    unittest.main()
