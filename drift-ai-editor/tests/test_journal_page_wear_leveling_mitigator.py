import unittest
from storage.journal_page_wear_leveling_mitigator import JournalPageWearLevelingMitigator


class TestJournalPageWearLevelingMitigator(unittest.TestCase):
    def test_staged_buffer_flushing(self):
        mitigator = JournalPageWearLevelingMitigator(target_coalesce_bytes=1024)
        
        # 500 bytes: não atinge o limiar
        should_flush1 = mitigator.stage_journal_entry(b"A" * 500)
        self.assertFalse(should_flush1)

        # Mais 600 bytes: total 1100 bytes >= 1024 (atinge limiar)
        should_flush2 = mitigator.stage_journal_entry(b"B" * 600)
        self.assertTrue(should_flush2)

        written = mitigator.flush_staged_buffer()
        self.assertEqual(written, 1100)

    def test_wear_savings_calculation(self):
        mitigator = JournalPageWearLevelingMitigator()
        res = mitigator.calculate_wear_savings(simulated_raw_writes_count=200, avg_write_size=1024)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["nand_write_amplification_reduction_pct"], 70.0)


if __name__ == "__main__":
    unittest.main()
