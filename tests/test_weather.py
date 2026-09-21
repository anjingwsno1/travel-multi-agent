import json
import unittest
from unittest.mock import MagicMock, patch

import requests

from tools.weather import get_weather


class GetWeatherTests(unittest.TestCase):
    @patch("tools.weather.requests.get")
    @patch("tools.weather.load_weather_api_key", return_value="weather-key")
    def test_returns_normalized_current_weather(self, mock_key, mock_get) -> None:
        response = MagicMock()
        response.json.return_value = {
            "location": {"name": "Shanghai", "country": "China"},
            "current": {
                "condition": {"text": "Sunny"},
                "temp_c": 25.0,
                "feelslike_c": 26.1,
            },
        }
        mock_get.return_value = response

        result = json.loads(get_weather.invoke({"location": "上海"}))

        mock_get.assert_called_once_with(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": "weather-key", "q": "上海", "aqi": "no", "alerts": "no"},
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(
            result,
            {
                "location": "Shanghai",
                "country": "China",
                "condition": "Sunny",
                "temperature_c": 25.0,
                "feelslike_c": 26.1,
            },
        )

    @patch("tools.weather.load_weather_api_key")
    def test_propagates_missing_key_error(self, mock_key) -> None:
        mock_key.side_effect = RuntimeError("WEATHER_API_KEY is required")

        with self.assertRaisesRegex(RuntimeError, "WEATHER_API_KEY is required"):
            get_weather.invoke({"location": "上海"})

    @patch("tools.weather.requests.get")
    @patch("tools.weather.load_weather_api_key", return_value="weather-key")
    def test_propagates_weather_service_error(self, mock_key, mock_get) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("401 Client Error")
        mock_get.return_value = response

        with self.assertRaisesRegex(requests.HTTPError, "401 Client Error"):
            get_weather.invoke({"location": "上海"})
