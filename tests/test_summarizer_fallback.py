import unittest

from services.ai_service import build_quick_response


class SummarizerFallbackTests(unittest.TestCase):
    def test_builds_quick_summary_response(self):
        prompt = "Summarize this text:\nHello world. This is a sample paragraph."

        reply = build_quick_response(prompt)

        self.assertIn("Summary:", reply)
        self.assertIn("Hello world", reply)


if __name__ == "__main__":
    unittest.main()
