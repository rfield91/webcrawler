import unittest
from crawl import get_images_from_html, get_urls_from_html, normalize_url, get_heading_from_html, get_first_paragraph_from_html

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
                print(f"Testing {test_case}")
                actual = normalize_url(test_case)
                self.assertEqual(actual, expected)

    def test_get_heading_from_html(self):
        test_cases = [
            {
                "title": "H1 only",
                "input": "<html><body><h1>Test Title</h1></body></html>",
                "expected": "Test Title"
            },
            {
                "title": "No H1",
                "input": "<html><body><p>Test no heading</p></body></html>",
                "expected": ""
            },
            {
                "title": "H2, no H1",
                "input": "<html><body><h2>Test h2</h2></body></html>",
                "expected": "Test h2"
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                print(f"Testing {test_case["title"]}")
                expected = test_case["expected"]
                actual = get_heading_from_html(test_case["input"])
                self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html(self):
        test_cases = [
            {
                "title": "One paragraph",
                "input": "<html><body><p>Test Paragraph</p></body></html>",
                "expected": "Test Paragraph"
            },
            {
                "title": "No paragraphs",
                "input": "<html><body><span>Test Paragraph</span></body></html>",
                "expected": ""
            },
            {
                "title": "Paragraph inside main",
                "input": "<html><body><main><p>Test Paragraph</p></main><p>Outside main</p></body></html>",
                "expected": "Test Paragraph"
            },
            {
                "title": "Paragraph before main",
                "input": "<html><body><p>Outside main</p><main><p>Test Paragraph</p></main></body></html>",
                "expected": "Test Paragraph"
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                print(f"Testing {test_case["title"]}")
                expected = test_case["expected"]
                actual = get_first_paragraph_from_html(test_case["input"])
                self.assertEqual(actual, expected)

    def test_get_urls_from_html(self):
        test_cases = [
            {
                "title": "One link",
                "html": '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": [
                    "https://crawler-test.com"
                ]
            },
            {
                "title": "One link, relative",
                "html": '<html><body><a href="/some/path"><span>Boot.dev</span></a></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": [
                    "https://crawler-test.com/some/path"
                ]
            },
            {
                "title": "Two links",
                "html": '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a><a href="/some/other/path"><span>Boot.dev2</span></a></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": [
                    "https://crawler-test.com",
                    "https://crawler-test.com/some/other/path",
                ]
            },
            {
                "title": "No links",
                "html": '<html><body><p>No Links</body></html>',
                "base_url": "https://crawler-test.com",
                "expected": []
            }
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                print(f"Testing {test_case["title"]}")
                expected = test_case["expected"]
                actual = get_urls_from_html(test_case["html"], test_case["base_url"])
                self.assertEqual(actual, expected)

    def test_get_images_from_html(self):
        test_cases = [
            {
                "title": "One image - relative",
                "html": '<html><body><img src="/logo.png" alt="Logo"></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": [
                    "https://crawler-test.com/logo.png"
                ]
            },
            {
                "title": "One image - absolute",
                "html": '<html><body><img src="https://crawler-test.com/logo.png" alt="Logo"></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": [
                    "https://crawler-test.com/logo.png"
                ]
            },
            {
                "title": "Two images",
                "html": '<html><body><img src="https://crawler-test.com/logo.png" alt="Logo"><img src="/logo-2.png" alt="Logo 2"></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": [
                    "https://crawler-test.com/logo.png",
                    "https://crawler-test.com/logo-2.png"
                ]
            },
            {
                "title": "No images",
                "html": '<html><body><p>No images</p></body></html>',
                "base_url": "https://crawler-test.com",
                "expected": []
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                print(f"Testing {test_case["title"]}")
                expected = test_case["expected"]
                actual = get_images_from_html(test_case["html"], test_case["base_url"])
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
