import unittest
from pipeline.zero_copy_frame_pipe_allocator import ZeroCopyFramePipeAllocator


class TestZeroCopyFramePipeAllocator(unittest.TestCase):
    def test_build_memory_pipe_pipeline(self):
        res = ZeroCopyFramePipeAllocator.build_memory_pipe_pipeline(width=1920, height=1080, fps=30.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intermediate_disk_write_bytes"], 0)
        self.assertEqual(res["ssd_io_saved_pct"], 100.0)
        self.assertIn("-f rawvideo", res["pipe_input_args"])


if __name__ == "__main__":
    unittest.main()
