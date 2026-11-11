import unittest
from media.chunked_direct_io_stream_writer import ChunkedDirectIOStreamWriter


class TestChunkedDirectIOStreamWriter(unittest.TestCase):
    def test_direct_io_accounting(self):
        writer = ChunkedDirectIOStreamWriter(target_chunk_bytes=1024 * 1024)
        writer.record_chunk_flush(1024 * 1024)
        writer.record_chunk_flush(1024 * 1024)

        self.assertEqual(writer._chunks_flushed, 2)
        self.assertEqual(writer._total_bytes_written, 2 * 1024 * 1024)

        calc = writer.calculate_ram_cache_preservation(export_total_mb=4096.0)
        self.assertEqual(calc["status"], "success")
        self.assertEqual(calc["system_ram_cache_saved_mb"], 4096.0)
        self.assertGreater(calc["swap_thrashing_prevention_pct"], 90.0)


if __name__ == "__main__":
    unittest.main()
