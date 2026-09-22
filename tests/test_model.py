import unittest
from unittest.mock import MagicMock, patch

from app.config import Settings
from app.model import ask_model, create_chat_model


class AskModelTests(unittest.TestCase):
    @patch("app.model.ChatOpenAI")
    @patch("app.model.load_settings", return_value=Settings(deepseek_api_key="test-key"))
    def test_invokes_configured_model_once(self, mock_settings, mock_chat_openai) -> None:
        response = MagicMock()
        response.content = "上海很适合旅行。"
        mock_chat_openai.return_value.invoke.return_value = response

        result = ask_model("上海适合旅行吗？")

        mock_chat_openai.assert_called_once_with(
            model="deepseek-flash",
            api_key="test-key",
            base_url="https://api.deepseek.com",
            extra_body={"thinking": {"type": "disabled"}},
        )
        mock_chat_openai.return_value.invoke.assert_called_once_with("上海适合旅行吗？")
        self.assertEqual(result, "上海很适合旅行。")

    @patch("app.model.ChatOpenAI")
    @patch("app.model.load_settings", return_value=Settings(deepseek_api_key="test-key"))
    def test_creates_deepseek_compatible_chat_model(self, mock_settings, mock_chat_openai) -> None:
        create_chat_model()

        mock_chat_openai.assert_called_once_with(
            model="deepseek-flash",
            api_key="test-key",
            base_url="https://api.deepseek.com",
            extra_body={"thinking": {"type": "disabled"}},
        )
