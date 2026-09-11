import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

# Append modules directory to sys.path without displacing sys.path[0]
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
modules_dir = os.path.join(project_root, "modules")
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import weather


class TestWeatherModule(unittest.TestCase):

    @patch("weather.requests.get")
    def test_get_weather_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = " Nairobi: ⛅️ +22°C \n"
        mock_get.return_value = mock_response

        result = weather.get_weather("  Nairobi  ")

        self.assertEqual(result, "Nairobi: ⛅️ +22°C")
        mock_get.assert_called_once_with(
            "https://wttr.in/Nairobi?format=3",
            timeout=10,
            headers={"User-Agent": "curl"},
        )

    @patch("weather.requests.get")
    def test_get_weather_html_response_guard(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<!DOCTYPE html><html><body>404 Not Found</body></html>"
        mock_get.return_value = mock_response

        result = weather.get_weather("London")

        self.assertEqual(
            result,
            "Weather service returned an invalid response. Please try again later.",
        )

    @patch("weather.requests.get")
    def test_get_weather_error_string_guard(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "ERR: Service overloaded"
        mock_get.return_value = mock_response

        result = weather.get_weather("Tokyo")

        self.assertEqual(
            result, "Weather service is temporarily unavailable."
        )

    @patch("weather.requests.get", side_effect=requests.Timeout)
    def test_get_weather_timeout(self, mock_get):
        result = weather.get_weather("Paris")
        self.assertEqual(result, "Weather request timed out.")

    @patch("weather.requests.get", side_effect=requests.ConnectionError)
    def test_get_weather_connection_error(self, mock_get):
        result = weather.get_weather("Berlin")
        self.assertEqual(result, "Unable to connect to weather service.")

    @patch(
        "weather.requests.get",
        side_effect=RuntimeError("Unexpected system failure"),
    )
    def test_get_weather_generic_exception(self, mock_get):
        result = weather.get_weather("Sydney")
        self.assertEqual(
            result, "Weather error: Unexpected system failure"
        )


if __name__ == "__main__":
    unittest.main()