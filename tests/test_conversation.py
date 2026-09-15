import os
import sys
import unittest

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import conversation


class TestConversationModule(unittest.TestCase):

    def setUp(self):
        # Clear history list state before each test run
        conversation.clear_history()

    def test_get_history_empty(self):
        self.assertEqual(conversation.get_history(), [])

    def test_add_message_and_get_history(self):
        conversation.add_message("user", "Hello Nova")
        conversation.add_message("assistant", "Greetings! How can I help?")

        history = conversation.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], {"role": "user", "content": "Hello Nova"})
        self.assertEqual(
            history[1],
            {"role": "assistant", "content": "Greetings! How can I help?"},
        )

    def test_add_message_sliding_window_limit(self):
        # Push 12 messages to verify sliding window keeps only the last 10
        for i in range(1, 13):
            conversation.add_message("user", f"Message {i}")

        history = conversation.get_history()
        self.assertEqual(len(history), 10)
        # First message should be Message 3 (Messages 1 & 2 popped)
        self.assertEqual(history[0]["content"], "Message 3")
        self.assertEqual(history[-1]["content"], "Message 12")

    def test_clear_history(self):
        conversation.add_message("user", "Test message")
        self.assertEqual(len(conversation.get_history()), 1)

        conversation.clear_history()
        self.assertEqual(conversation.get_history(), [])


if __name__ == "__main__":
    unittest.main()