import os
import unittest
from unittest.mock import patch

from app.config import load_settings
from app.config import load_ark_api_key
from app.tracing import configure_langsmith


class LoadSettingsTests(unittest.TestCase):
    @patch("app.config.load_dotenv")
    def test_returns_deepseek_key_from_environment(self, mock_load_dotenv) -> None:
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            settings = load_settings()
        self.assertEqual(settings.deepseek_api_key, "test-key")

    @patch("app.config.load_dotenv")
    def test_raises_when_deepseek_key_is_missing(self, mock_load_dotenv) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DEEPSEEK_API_KEY is required"):
                load_settings()

    @patch("app.config.load_dotenv")
    def test_returns_ark_key_from_environment(self, mock_load_dotenv) -> None:
        with patch.dict(os.environ, {"ARK_API_KEY": "ark-key"}, clear=True):
            self.assertEqual(load_ark_api_key(), "ark-key")

    @patch("app.tracing.load_dotenv")
    def test_enables_langsmith_when_api_key_is_set(self, mock_load_dotenv) -> None:
        with patch.dict(os.environ, {"LANGSMITH_API_KEY": "smith-key"}, clear=True):
            self.assertTrue(configure_langsmith())
            self.assertEqual(os.environ["LANGSMITH_TRACING"], "true")
            self.assertEqual(os.environ["LANGSMITH_PROJECT"], "travel-multi-agent")

    @patch("app.tracing.load_dotenv")
    def test_keeps_langsmith_disabled_without_api_key(self, mock_load_dotenv) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(configure_langsmith())
