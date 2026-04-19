import unittest

from app.utils import extract_json_object, normalize_whitespace, safe_truncate


class UtilsTests(unittest.TestCase):
    def test_extract_json_from_fenced_block(self):
        payload = """```json
{"approved": true, "feedback": "ok", "missing_points": []}
```"""
        data = extract_json_object(payload)
        self.assertTrue(data["approved"])
        self.assertEqual(data["feedback"], "ok")

    def test_extract_json_from_wrapped_text(self):
        payload = "Here you go: {\"value\": 42, \"name\": \"demo\"}"
        data = extract_json_object(payload)
        self.assertEqual(data["value"], 42)
        self.assertEqual(data["name"], "demo")

    def test_safe_truncate(self):
        text = "hello world " * 30
        clipped = safe_truncate(text, 30)
        self.assertTrue(len(clipped) <= 30)
        self.assertTrue(clipped.endswith("..."))

    def test_normalize_whitespace(self):
        self.assertEqual(normalize_whitespace("a   b\n\t c"), "a b c")


if __name__ == "__main__":
    unittest.main()
