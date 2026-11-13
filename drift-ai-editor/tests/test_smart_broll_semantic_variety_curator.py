import unittest
from pipeline.smart_broll_semantic_variety_curator import SmartBrollSemanticVarietyCurator


class TestSmartBrollSemanticVarietyCurator(unittest.TestCase):
    def test_evaluate_sequence_diversity(self):
        diverse = ["WIDE", "MEDIUM", "CLOSE", "DYNAMIC"]
        repeated = ["WIDE", "WIDE", "WIDE", "WIDE"]
        self.assertEqual(SmartBrollSemanticVarietyCurator.evaluate_sequence_diversity(diverse), 100.0)
        self.assertEqual(SmartBrollSemanticVarietyCurator.evaluate_sequence_diversity(repeated), 0.0)

    def test_curate_broll_sequence(self):
        res = SmartBrollSemanticVarietyCurator.curate_broll_sequence()
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["curated_diversity_score_pct"], res["initial_diversity_score_pct"])
        self.assertEqual(len(res["curated_sequence"]), 5)

    def test_benchmark_curator_performance(self):
        bench = SmartBrollSemanticVarietyCurator.benchmark_curator_performance()
        self.assertEqual(bench["status"], "success")
        self.assertLess(bench["execution_time_ms"], 1.0)


if __name__ == "__main__":
    unittest.main()
