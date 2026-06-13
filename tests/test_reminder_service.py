import unittest

from services.reminder_service import build_reminder_message


class ReminderServiceTests(unittest.TestCase):
    def test_build_reminder_message_contains_task_and_due_time(self):
        message = build_reminder_message("Submit report", "2026-06-12 14:00")

        self.assertIn("Submit report", message)
        self.assertIn("2026-06-12 14:00", message)


if __name__ == "__main__":
    unittest.main()
