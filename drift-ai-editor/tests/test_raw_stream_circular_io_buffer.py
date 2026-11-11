import unittest
from media.raw_stream_circular_io_buffer import RawStreamCircularIOBuffer


class TestRawStreamCircularIOBuffer(unittest.TestCase):
    def test_circular_write_and_read(self):
        buf = RawStreamCircularIOBuffer(capacity_bytes=100)
        data = b"Hello Stream Zero Disk I/O"
        written = buf.write_stream_chunk(data)
        self.assertEqual(written, len(data))

        read_data = buf.read_stream_chunk(len(data))
        self.assertEqual(read_data, data)

        savings = buf.get_io_savings()
        self.assertEqual(savings["status"], "success")
        self.assertEqual(savings["temporary_files_created"], 0)
        self.assertEqual(savings["total_streamed_bytes"], len(data))


if __name__ == "__main__":
    unittest.main()
