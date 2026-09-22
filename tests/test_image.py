import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools.image import generate_image


class GenerateImageTests(unittest.TestCase):
    @patch("tools.image.requests.get")
    @patch("tools.image.OpenAI")
    @patch("tools.image.load_ark_api_key", return_value="ark-key")
    def test_generates_downloads_and_saves_image(self, mock_key, mock_openai, mock_get) -> None:
        generated = MagicMock()
        generated.data = [MagicMock(url="https://example.com/image.png")]
        mock_openai.return_value.images.generate.return_value = generated
        download = MagicMock()
        download.content = b"image-bytes"
        mock_get.return_value = download

        with patch("tools.image.Path.write_bytes") as mock_write_bytes:
            image_path = Path(generate_image.invoke({"prompt": "上海外滩日落"}))

        self.assertEqual(image_path.parent.name, "images")
        mock_write_bytes.assert_called_once_with(b"image-bytes")

        mock_openai.assert_called_once_with(
            api_key="ark-key",
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        mock_openai.return_value.images.generate.assert_called_once_with(
            model="doubao-seedream-5-0-lite-260128",
            prompt="上海外滩日落",
            size="1024x1024",
            response_format="url",
        )
        mock_get.assert_called_once_with("https://example.com/image.png", timeout=30)
        download.raise_for_status.assert_called_once_with()

    @patch("tools.image.OpenAI")
    @patch("tools.image.load_ark_api_key", return_value="ark-key")
    def test_raises_when_service_returns_no_image_url(self, mock_key, mock_openai) -> None:
        generated = MagicMock()
        generated.data = [MagicMock(url=None)]
        mock_openai.return_value.images.generate.return_value = generated

        with self.assertRaisesRegex(RuntimeError, "未返回图片 URL"):
            generate_image.invoke({"prompt": "上海外滩日落"})

    @patch("tools.image.load_ark_api_key")
    def test_propagates_missing_ark_key_error(self, mock_key) -> None:
        mock_key.side_effect = RuntimeError("ARK_API_KEY is required")

        with self.assertRaisesRegex(RuntimeError, "ARK_API_KEY is required"):
            generate_image.invoke({"prompt": "上海外滩日落"})
