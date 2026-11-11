import unittest
from core.ram_working_set_trimmer import RamWorkingSetTrimmer


class TestRamWorkingSetTrimmer(unittest.TestCase):
    def test_trim_working_set(self):
        res = RamWorkingSetTrimmer.trim_working_set()
        self.assertEqual(res["status"], "success")
        self.assertIn("python_gc_objects_freed", res)
        self.assertIn("win32_empty_working_set_applied", res)


if __name__ == "__main__":
    unittest.main()
