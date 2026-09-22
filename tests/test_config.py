import os
import unittest
from unittest.mock import patch

from app.config import load_settings
from app.config import load_ark_api_key


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
