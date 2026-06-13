import unittest

from services.ai_service import summarize_text


class SummarizeTextTests(unittest.TestCase):
    def test_summarize_text_returns_short_summary(self):
        text = "This is the first sentence. This is the second sentence. This is the third sentence."

        summary = summarize_text(text)

        self.assertIn("first sentence", summary)
        self.assertIn("second sentence", summary)


if __name__ == "__main__":
    unittest.main()
