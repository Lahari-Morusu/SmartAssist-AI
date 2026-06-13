import unittest
from unittest.mock import patch
import requests

from services.ai_service import ask_ai, build_quick_response, build_unavailable_message, translate_text


class AskAITests(unittest.TestCase):
    @patch("services.ai_service.requests.post")
    def test_returns_response_from_ollama(self, mock_post):
        mock_post.return_value.json.return_value = {"response": "Bonjour"}

        self.assertEqual(ask_ai("Draft a detailed response about the launch timeline"), "Bonjour")

    @patch("services.ai_service.requests.post", side_effect=requests.exceptions.ConnectionError("boom"))
    def test_returns_fallback_on_connection_error(self, mock_post):
        result = ask_ai("Draft a detailed response about the launch timeline")

        self.assertIn("unavailable", result.lower())

    @patch("services.ai_service.requests.post", side_effect=requests.exceptions.Timeout("boom"))
    def test_returns_generic_fallback_on_timeout(self, mock_post):
        result = ask_ai("Explain the weather")

        self.assertIn("unavailable", result.lower())

    @patch("services.ai_service.requests.post", side_effect=requests.exceptions.Timeout("boom"))
    def test_returns_structured_email_fallback_on_timeout(self, mock_post):
        result = ask_ai("Write a professional email about requesting a meeting next week")

        self.assertIn("Subject:", result)
        self.assertIn("Best regards", result)

    def test_does_not_use_generic_chat_reply_for_short_questions(self):
        result = build_quick_response("What is the weather today?")

        self.assertIsNone(result)

    def test_does_not_preempt_email_generation(self):
        result = build_quick_response("Write a professional email about requesting a meeting next week")

        self.assertIsNone(result)

    def test_builds_helpful_unavailable_message(self):
        result = build_unavailable_message("What is the weather today?")

        self.assertIn("unavailable", result.lower())

    def test_translation_requests_do_not_use_quick_preview(self):
        prompt = "Translate the following text from English to Telugu.\n\nText:\nHello"

        self.assertIsNone(build_quick_response(prompt))

    @patch("services.ai_service.requests.post")
    def test_translate_text_avoids_echoing_source_text(self, mock_post):
        mock_post.return_value.json.return_value = {"response": "Hello"}

        result = translate_text("Hello", "English", "Telugu")

        self.assertNotEqual(result.strip().lower(), "hello")
        self.assertTrue(result.strip())

    def test_translate_text_uses_phrase_fallback_for_known_sentence(self):
        result = translate_text("I ran to the station but missed the train because it was already late.", "English", "Telugu")

        self.assertIn("స్టేషన్", result)
        self.assertIn("రైలు", result)

    def test_builds_quick_chat_response_for_greetings(self):
        reply = build_quick_response("hello there")

        self.assertIn("Hello", reply)


if __name__ == "__main__":
    unittest.main()
