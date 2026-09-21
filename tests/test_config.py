import os
import unittest
from unittest.mock import patch

from app.config import load_settings


class LoadSettingsTests(unittest.TestCase):
    def test_returns_deepseek_key_from_environment(self) -> None:
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            settings = load_settings()
        self.assertEqual(settings.deepseek_api_key, "test-key")

    def test_raises_when_deepseek_key_is_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DEEPSEEK_API_KEY is required"):
                load_settings()
