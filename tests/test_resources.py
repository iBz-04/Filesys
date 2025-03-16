import unittest
from src.resources import list_files, read_file

class TestResources(unittest.TestCase):
    def test_list_files(self):
        result = list_files()
        self.assertIn("files", result)

    def test_read_file(self):
        result = read_file("test.txt")
        self.assertIn("content", result)

if __name__ == "__main__":
    unittest.main()