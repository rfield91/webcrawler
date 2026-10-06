import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html

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

    def test_get_heading_from_html(self):
        test_cases = [
            {
                "input": "<html><body><h1>Test Title</h1></body></html>",
                "expected": "Test Title"
            },
            {
                "input": "<html><body><p>Test no heading</p></body></html>",
                "expected": ""
            },
            {
                "input": "<html><body><h2>Test h2</h2></body></html>",
                "expected": "Test h2"
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                expected = test_case["expected"]
                actual = get_heading_from_html(test_case["input"])
                self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html(self):
        test_cases = [
            {
                "input": "<html><body><p>Test Paragraph</p></body></html>",
                "expected": "Test Paragraph"
            },
            {
                "input": "<html><body><span>Test Paragraph</span></body></html>",
                "expected": ""
            },
            {
                "input": "<html><body><main><p>Test Paragraph</p></main><p>Outside main</p></body></html>",
                "expected": "Test Paragraph"
            },
            {
                "input": "<html><body><p>Outside main</p><main><p>Test Paragraph</p></main></body></html>",
                "expected": "Test Paragraph"
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                expected = test_case["expected"]
                actual = get_first_paragraph_from_html(test_case["input"])
                self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
