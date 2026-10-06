import unittest
from crawl import normalize_url

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        test_cases = [
            "https://www.boot.dev/blog/path/",
            "https://www.boot.dev/blog/path",
            "http://www.boot.dev/blog/path/",
            "http://www.boot.dev/blog/path",
            "http://boot.dev/blog/path/",
            "boot.dev/blog/path/",
            "boot.dev/blog/path",
        ]

        expected = "www.boot.dev/blog/path"

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                actual = normalize_url(test_case)
                self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
