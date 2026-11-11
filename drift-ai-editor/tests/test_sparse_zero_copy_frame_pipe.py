import unittest
from storage.sparse_zero_copy_frame_pipe import SparseZeroCopyFramePipe


class TestSparseZeroCopyFramePipe(unittest.TestCase):
    def setUp(self):
        self.pipe = SparseZeroCopyFramePipe(frame_width=640, frame_height=360, bytes_per_pixel=4, pool_depth=2)

    def test_buffer_recycling(self):
        buf1 = self.pipe.acquire_frame_buffer()
        buf2 = self.pipe.acquire_frame_buffer()
        buf3 = self.pipe.acquire_frame_buffer()

        self.assertIs(buf1, buf3)  # Pool depth 2 recicla o primeiro buffer no 3º acquire
        metrics = self.pipe.get_pipe_metrics()
        self.assertEqual(metrics["frames_served_zero_copy"], 3)
        self.assertGreater(metrics["ram_churn_prevented_mb"], 0.0)


if __name__ == "__main__":
    unittest.main()
