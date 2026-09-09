import unittest
from unittest.mock import patch
from modules.apps import open_app


class TestOpenAppNativeApplications(unittest.TestCase):

    @patch("modules.apps.os.system")
    def test_open_notepad(self, mock_system):
        result = open_app("notepad")

        mock_system.assert_called_once_with("start notepad")
        self.assertEqual(result, "Opening notepad...")

    @patch("modules.apps.os.system")
    def test_open_calculator(self, mock_system):
        result = open_app("calculator")

        mock_system.assert_called_once_with("start calc")
        self.assertEqual(result, "Opening calculator...")

    @patch("modules.apps.os.system")
    def test_open_paint(self, mock_system):
        result = open_app("paint")

        mock_system.assert_called_once_with("start mspaint")
        self.assertEqual(result, "Opening paint...")

    @patch("modules.apps.os.system")
    def test_open_chrome(self, mock_system):
        result = open_app("chrome")

        mock_system.assert_called_once_with("start chrome")
        self.assertEqual(result, "Opening chrome...")

    @patch("modules.apps.os.system")
    def test_open_explorer(self, mock_system):
        result = open_app("explorer")

        mock_system.assert_called_once_with("start explorer")
        self.assertEqual(result, "Opening explorer...")

    @patch("modules.apps.os.system")
    def test_open_vscode(self, mock_system):
        result = open_app("vscode")

        mock_system.assert_called_once_with("start code")
        self.assertEqual(result, "Opening vscode...")


class TestOpenAppWebApplications(unittest.TestCase):

    @patch("modules.apps.os.system")
    def test_open_youtube(self, mock_system):
        result = open_app("youtube")

        mock_system.assert_called_once_with(
            "start https://www.youtube.com"
        )
        self.assertEqual(result, "Opening youtube...")

    @patch("modules.apps.os.system")
    def test_open_gmail(self, mock_system):
        result = open_app("gmail")

        mock_system.assert_called_once_with(
            "start https://mail.google.com"
        )
        self.assertEqual(result, "Opening gmail...")

    @patch("modules.apps.os.system")
    def test_open_github(self, mock_system):
        result = open_app("github")

        mock_system.assert_called_once_with(
            "start https://github.com"
        )
        self.assertEqual(result, "Opening github...")

    @patch("modules.apps.os.system")
    def test_open_chatgpt(self, mock_system):
        result = open_app("chatgpt")

        mock_system.assert_called_once_with(
            "start https://chatgpt.com"
        )
        self.assertEqual(result, "Opening chatgpt...")

    @patch("modules.apps.os.system")
    def test_open_google(self, mock_system):
        result = open_app("google")

        mock_system.assert_called_once_with(
            "start https://www.google.com"
        )
        self.assertEqual(result, "Opening google...")


class TestOpenAppInputHandling(unittest.TestCase):

    @patch("modules.apps.os.system")
    def test_application_name_is_case_insensitive(self, mock_system):
        result = open_app("NoTePaD")

        mock_system.assert_called_once_with("start notepad")
        self.assertEqual(result, "Opening notepad...")

    @patch("modules.apps.os.system")
    def test_uppercase_web_application_is_normalized(self, mock_system):
        result = open_app("YOUTUBE")

        mock_system.assert_called_once_with(
            "start https://www.youtube.com"
        )
        self.assertEqual(result, "Opening youtube...")

    @patch("modules.apps.os.system")
    def test_unknown_application_returns_unknown_message(
        self,
        mock_system,
    ):
        result = open_app("spotify")

        mock_system.assert_not_called()
        self.assertEqual(result, "Unknown application.")

    @patch("modules.apps.os.system")
    def test_empty_application_name_returns_unknown_message(
        self,
        mock_system,
    ):
        result = open_app("")

        mock_system.assert_not_called()
        self.assertEqual(result, "Unknown application.")


class TestOpenAppErrors(unittest.TestCase):

    @patch("modules.apps.os.system")
    def test_system_error_returns_error_message(self, mock_system):
        mock_system.side_effect = OSError("Launch failed")

        result = open_app("notepad")

        self.assertEqual(
            result,
            "Error opening application: Launch failed",
        )

    @patch("modules.apps.os.system")
    def test_generic_system_error_is_caught(self, mock_system):
        mock_system.side_effect = RuntimeError("System failure")

        result = open_app("chrome")

        self.assertEqual(
            result,
            "Error opening application: System failure",
        )

    @patch("modules.apps.os.system")
    def test_error_message_preserves_original_exception_text(
        self,
        mock_system,
    ):
        mock_system.side_effect = Exception("Custom launch error")

        result = open_app("github")

        self.assertIn("Custom launch error", result)
        self.assertTrue(
            result.startswith("Error opening application:")
        )


class TestOpenAppSupportedApplications(unittest.TestCase):

    @patch("modules.apps.os.system")
    def test_all_supported_applications_have_expected_commands(
        self,
        mock_system,
    ):
        expected_commands = {
            "notepad": "start notepad",
            "calculator": "start calc",
            "paint": "start mspaint",
            "chrome": "start chrome",
            "explorer": "start explorer",
            "vscode": "start code",
            "youtube": "start https://www.youtube.com",
            "gmail": "start https://mail.google.com",
            "github": "start https://github.com",
            "chatgpt": "start https://chatgpt.com",
            "google": "start https://www.google.com",
        }

        for app_name, expected_command in expected_commands.items():
            with self.subTest(app_name=app_name):
                mock_system.reset_mock()

                result = open_app(app_name)

                mock_system.assert_called_once_with(
                    expected_command
                )
                self.assertEqual(
                    result,
                    f"Opening {app_name}...",
                )


if __name__ == "__main__":
    unittest.main()