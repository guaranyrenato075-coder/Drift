import unittest
from media.speculative_disk_seek_canceller import SpeculativeDiskSeekCanceller


class TestSpeculativeDiskSeekCanceller(unittest.TestCase):
    def test_prune_obsolete_requests(self):
        canceller = SpeculativeDiskSeekCanceller()
        canceller.register_read_request("clip_1", 100.0)
        canceller.register_read_request("clip_2", 100.1)
        canceller.register_read_request("clip_3", 100.2)

        # O usuário rolou a tela e apenas o clip_3 está visível
        visible = {"clip_3"}
        res = canceller.prune_obsolete_requests(visible)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["cancelled_obsolete_seeks"], 2)
        self.assertEqual(res["active_seeks_remaining"], 1)
        self.assertIn("clip_1", res["cancelled_clip_ids"])
        self.assertIn("clip_2", res["cancelled_clip_ids"])


if __name__ == "__main__":
    unittest.main()
