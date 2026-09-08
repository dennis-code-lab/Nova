"""
Nova Engine v137
AI Module Tests

Verifies API-key discovery, Gemini client initialization,
standard AI inference, configurable AI inference, fallback
behavior, empty responses, and exception handling.
"""
import json
import os
import unittest
from unittest.mock import Mock, mock_open, patch

import modules.ai as ai


class TestDiscoverApiKey(unittest.TestCase):

    def setUp(self):
        self.original_gemini_key = os.environ.pop(
            "GEMINI_API_KEY",
            None,
        )
        self.original_google_key = os.environ.pop(
            "GOOGLE_API_KEY",
            None,
        )

    def tearDown(self):
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GOOGLE_API_KEY", None)

        if self.original_gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = (
                self.original_gemini_key
            )

        if self.original_google_key is not None:
            os.environ["GOOGLE_API_KEY"] = (
                self.original_google_key
            )

    def test_gemini_api_key_is_preferred(self):
        os.environ["GEMINI_API_KEY"] = "gemini-key"
        os.environ["GOOGLE_API_KEY"] = "google-key"

        with patch(
            "modules.ai.os.path.exists",
            return_value=False,
        ):
            result = ai._discover_api_key()

        self.assertEqual(result, "gemini-key")

    def test_google_api_key_is_used_when_gemini_key_is_missing(
        self,
    ):
        os.environ["GOOGLE_API_KEY"] = "google-key"

        with patch(
            "modules.ai.os.path.exists",
            return_value=False,
        ):
            result = ai._discover_api_key()

        self.assertEqual(result, "google-key")

    def test_empty_gemini_key_is_ignored(self):
        os.environ["GEMINI_API_KEY"] = ""
        os.environ["GOOGLE_API_KEY"] = "google-key"

        with patch(
            "modules.ai.os.path.exists",
            return_value=False,
        ):
            result = ai._discover_api_key()

        self.assertEqual(result, "google-key")

    def test_empty_google_key_is_ignored(self):
        os.environ["GOOGLE_API_KEY"] = ""

        with patch(
            "modules.ai.os.path.exists",
            return_value=False,
        ):
            result = ai._discover_api_key()

        self.assertIsNone(result)

    def test_config_gemini_api_key_is_discovered(self):
        config = {
            "gemini_api_key": "config-gemini-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, False],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(config),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(
            result,
            "config-gemini-key",
        )

    def test_config_api_key_is_discovered(self):
        config = {
            "api_key": "config-api-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, False],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(config),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(
            result,
            "config-api-key",
        )

    def test_config_gemini_key_is_discovered(self):
        config = {
            "gemini_key": "config-gemini-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, False],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(config),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(
            result,
            "config-gemini-key",
        )

    def test_config_uppercase_gemini_api_key_is_discovered(
        self,
    ):
        config = {
            "GEMINI_API_KEY": "uppercase-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, False],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(config),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(
            result,
            "uppercase-key",
        )

    def test_config_key_variants_are_checked_in_order(self):
        config = {
            "gemini_api_key": "first-key",
            "api_key": "second-key",
            "gemini_key": "third-key",
            "GEMINI_API_KEY": "fourth-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, False],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(config),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(result, "first-key")

    def test_empty_config_value_is_skipped(self):
        config = {
            "gemini_api_key": "",
            "api_key": "fallback-config-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, False],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(config),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(
            result,
            "fallback-config-key",
        )

    def test_memory_api_key_is_discovered(self):
        memory = {
            "api_key": "memory-key",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[False, True],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(memory),
            ),
        ):
            result = ai._discover_api_key()

        self.assertEqual(result, "memory-key")

    def test_missing_files_return_none(self):
        with patch(
            "modules.ai.os.path.exists",
            return_value=False,
        ):
            result = ai._discover_api_key()

        self.assertIsNone(result)

    def test_invalid_config_json_returns_none(self):
        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, True],
        ), patch(
            "builtins.open",
            mock_open(
                read_data="{invalid json",
            ),
        ):
            result = ai._discover_api_key()

        self.assertIsNone(result)

    def test_invalid_config_can_fall_back_to_memory(self):
        memory = {
            "api_key": "memory-fallback",
        }

        mocked_open = mock_open(
            read_data="{invalid json",
        )

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[True, True],
        ), patch(
            "builtins.open",
            mocked_open,
        ):
            mocked_open.side_effect = [
                mock_open(
                    read_data="{invalid json",
                ).return_value,
                mock_open(
                    read_data=json.dumps(memory),
                ).return_value,
            ]

            result = ai._discover_api_key()

        self.assertEqual(
            result,
            "memory-fallback",
        )

    def test_memory_without_api_key_returns_none(self):
        memory = {
            "other": "value",
        }

        with patch(
            "modules.ai.os.path.exists",
            side_effect=[False, True],
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(memory),
            ),
        ):
            result = ai._discover_api_key()

        self.assertIsNone(result)

    def test_invalid_memory_json_returns_none(self):
        with patch(
            "modules.ai.os.path.exists",
            side_effect=[False, True],
        ), patch(
            "builtins.open",
            mock_open(
                read_data="{invalid json",
            ),
        ):
            result = ai._discover_api_key()

        self.assertIsNone(result)


class TestInitializeNova(unittest.TestCase):

    def setUp(self):
        ai._client = None

    def tearDown(self):
        ai._client = None

    def test_initialize_with_discovered_key_creates_client_with_key(
        self,
    ):
        client = Mock()

        with patch(
            "modules.ai._discover_api_key",
            return_value="test-key",
        ), patch(
            "modules.ai.genai.Client",
            return_value=client,
        ) as client_class:
            ai.initialize_nova()

        client_class.assert_called_once_with(
            api_key="test-key",
        )
        self.assertIs(ai._client, client)

    def test_initialize_with_key_sets_gemini_environment_variable(
        self,
    ):
        with patch(
            "modules.ai._discover_api_key",
            return_value="test-key",
        ), patch(
            "modules.ai.genai.Client",
            return_value=Mock(),
        ):
            os.environ.pop("GEMINI_API_KEY", None)

            ai.initialize_nova()

            self.assertEqual(
                os.environ["GEMINI_API_KEY"],
                "test-key",
            )

            os.environ.pop("GEMINI_API_KEY", None)

    def test_initialize_without_key_uses_default_client(
        self,
    ):
        client = Mock()

        with patch(
            "modules.ai._discover_api_key",
            return_value=None,
        ), patch(
            "modules.ai.genai.Client",
            return_value=client,
        ) as client_class:
            ai.initialize_nova()

        client_class.assert_called_once_with()
        self.assertIs(ai._client, client)

    def test_initialize_client_failure_raises_runtime_warning(
        self,
    ):
        with patch(
            "modules.ai._discover_api_key",
            return_value="bad-key",
        ), patch(
            "modules.ai.genai.Client",
            side_effect=Exception("connection failed"),
        ):
            with self.assertRaises(RuntimeWarning) as context:
                ai.initialize_nova()

        self.assertIn(
            "GenAI Client failed to initialize",
            str(context.exception),
        )

    def test_initialize_failure_does_not_leave_client_initialized(
        self,
    ):
        with patch(
            "modules.ai._discover_api_key",
            return_value="bad-key",
        ), patch(
            "modules.ai.genai.Client",
            side_effect=Exception("failure"),
        ):
            with self.assertRaises(RuntimeWarning):
                ai.initialize_nova()

        self.assertIsNone(ai._client)


class TestAskAI(unittest.TestCase):

    def setUp(self):
        ai._client = None

    def tearDown(self):
        ai._client = None

    def test_ask_ai_initializes_when_client_is_missing(self):
        client = Mock()

        response = Mock()
        response.text = "  Hello Nova  "

        client.models.generate_content.return_value = (
            response
        )

        with patch(
            "modules.ai.initialize_nova",
            side_effect=lambda: setattr(
                ai,
                "_client",
                client,
            ),
        ) as initialize:
            result = ai.ask_ai("Hello")

        initialize.assert_called_once()
        self.assertEqual(result, "Hello Nova")

    def test_ask_ai_uses_existing_client_without_initializing(
        self,
    ):
        client = Mock()

        response = Mock()
        response.text = "  Existing client response  "

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        with patch(
            "modules.ai.initialize_nova",
        ) as initialize:
            result = ai.ask_ai("Test prompt")

        initialize.assert_not_called()
        self.assertEqual(
            result,
            "Existing client response",
        )

    def test_ask_ai_uses_default_model(self):
        client = Mock()

        response = Mock()
        response.text = "Generated response"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        result = ai.ask_ai("Test prompt")

        client.models.generate_content.assert_called_once_with(
            model=ai._DEFAULT_MODEL,
            contents="Test prompt",
        )

        self.assertEqual(
            result,
            "Generated response",
        )

    def test_ask_ai_strips_response_text(self):
        client = Mock()

        response = Mock()
        response.text = "\n  Generated text  \n"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        result = ai.ask_ai("Prompt")

        self.assertEqual(
            result,
            "Generated text",
        )

    def test_ask_ai_returns_empty_response_error_message(self):
        client = Mock()

        response = Mock()
        response.text = ""

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        result = ai.ask_ai("Prompt")

        self.assertEqual(
            result,
            "Nova Engine Error: Model returned an empty generation response block.",
        )

    def test_ask_ai_returns_empty_response_error_when_response_is_none(
        self,
    ):
        client = Mock()

        client.models.generate_content.return_value = None

        ai._client = client

        result = ai.ask_ai("Prompt")

        self.assertEqual(
            result,
            "Nova Engine Error: Model returned an empty generation response block.",
        )

    def test_ask_ai_handles_generation_exception(self):
        client = Mock()

        client.models.generate_content.side_effect = Exception(
            "API unavailable",
        )

        ai._client = client

        result = ai.ask_ai("Prompt")

        self.assertIn(
            "Core Inference Error",
            result,
        )
        self.assertIn(
            "API unavailable",
            result,
        )


class TestAskAIWithConfig(unittest.TestCase):

    def setUp(self):
        ai._client = None

    def tearDown(self):
        ai._client = None

    def test_configured_ai_initializes_when_client_is_missing(
        self,
    ):
        client = Mock()

        response = Mock()
        response.text = "Configured response"

        client.models.generate_content.return_value = (
            response
        )

        with patch(
            "modules.ai.initialize_nova",
            side_effect=lambda: setattr(
                ai,
                "_client",
                client,
            ),
        ) as initialize, patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=Mock(),
        ):
            result = ai.ask_ai_with_config(
                "Prompt",
            )

        initialize.assert_called_once()

        self.assertEqual(
            result,
            "Configured response",
        )

    def test_configured_ai_uses_existing_client(self):
        client = Mock()

        response = Mock()
        response.text = "Existing configured response"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        with patch(
            "modules.ai.initialize_nova",
        ) as initialize, patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=Mock(),
        ):
            result = ai.ask_ai_with_config(
                "Prompt",
            )

        initialize.assert_not_called()

        self.assertEqual(
            result,
            "Existing configured response",
        )

    def test_configured_ai_builds_generation_config(
        self,
    ):
        client = Mock()

        response = Mock()
        response.text = "Response"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        config = Mock()

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=config,
        ) as config_class:
            ai.ask_ai_with_config(
                "Prompt",
                temperature=0.25,
                max_tokens=500,
            )

        config_class.assert_called_once_with(
            temperature=0.25,
            max_output_tokens=500,
        )

    def test_configured_ai_passes_config_to_generation(
        self,
    ):
        client = Mock()

        response = Mock()
        response.text = "Configured response"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        config = Mock()

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=config,
        ):
            ai.ask_ai_with_config(
                "Prompt",
                temperature=0.4,
                max_tokens=250,
            )

        client.models.generate_content.assert_called_once_with(
            model=ai._DEFAULT_MODEL,
            contents="Prompt",
            config=config,
        )

    def test_configured_ai_strips_response_text(self):
        client = Mock()

        response = Mock()
        response.text = "\n  Configured response  \n"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=Mock(),
        ):
            result = ai.ask_ai_with_config(
                "Prompt",
            )

        self.assertEqual(
            result,
            "Configured response",
        )

    def test_configured_ai_returns_empty_string_for_empty_text(
        self,
    ):
        client = Mock()

        response = Mock()
        response.text = ""

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=Mock(),
        ):
            result = ai.ask_ai_with_config(
                "Prompt",
            )

        self.assertEqual(result, "")

    def test_configured_ai_returns_empty_string_when_text_is_none(
        self,
    ):
        client = Mock()

        response = Mock()
        response.text = None

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=Mock(),
        ):
            result = ai.ask_ai_with_config(
                "Prompt",
            )

        self.assertEqual(result, "")

    def test_configured_ai_handles_generation_exception(
        self,
    ):
        client = Mock()

        client.models.generate_content.side_effect = Exception(
            "configured API failure",
        )

        ai._client = client

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=Mock(),
        ):
            result = ai.ask_ai_with_config(
                "Prompt",
            )

        self.assertIn(
            "Config Inference Error",
            result,
        )
        self.assertIn(
            "configured API failure",
            result,
        )

    def test_default_configuration_values_are_used(self):
        client = Mock()

        response = Mock()
        response.text = "Default configuration response"

        client.models.generate_content.return_value = (
            response
        )

        ai._client = client

        config = Mock()

        with patch(
            "modules.ai.types.GenerateContentConfig",
            return_value=config,
        ) as config_class:
            ai.ask_ai_with_config("Prompt")

        config_class.assert_called_once_with(
            temperature=0.7,
            max_output_tokens=1000,
        )


if __name__ == "__main__":
    unittest.main()