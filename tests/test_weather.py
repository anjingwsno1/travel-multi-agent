import json
import unittest
from unittest.mock import MagicMock, patch

import requests

from tools.weather import get_weather


class GetWeatherTests(unittest.TestCase):
    @patch("tools.weather.requests.get")
    def test_returns_current_weather_and_three_day_forecast(self, mock_get) -> None:
        geocoding_response = MagicMock()
        geocoding_response.json.return_value = {
            "results": [{"name": "上海", "country": "中国", "latitude": 31.23, "longitude": 121.47}]
        }
        weather_response = MagicMock()
        weather_response.json.return_value = {
            "current": {"weather_code": 0, "temperature_2m": 25.0, "apparent_temperature": 26.1},
            "daily": {
                "time": ["2026-09-22", "2026-09-23", "2026-09-24"],
                "weather_code": [0, 3, 61],
                "temperature_2m_max": [28.0, 27.0, 24.0],
                "temperature_2m_min": [20.0, 21.0, 19.0],
                "precipitation_probability_max": [0, 10, 60],
            },
        }
        mock_get.side_effect = [geocoding_response, weather_response]

        result = json.loads(get_weather.invoke({"location": "上海"}))

        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(result["location"], "上海")
        self.assertEqual(result["current"]["condition"], "晴")
        self.assertEqual(result["forecast"][2]["condition"], "雨")
        self.assertEqual(len(result["forecast"]), 3)

    @patch("tools.weather.requests.get")
    def test_raises_when_location_is_not_found(self, mock_get) -> None:
        geocoding_response = MagicMock()
        geocoding_response.json.return_value = {"results": []}
        mock_get.return_value = geocoding_response

        with self.assertRaisesRegex(ValueError, "未找到地点"):
            get_weather.invoke({"location": "不存在的地点"})

    @patch("tools.weather.requests.get")
    def test_propagates_weather_service_error(self, mock_get) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("503 Service Unavailable")
        mock_get.return_value = response

        with self.assertRaisesRegex(requests.HTTPError, "503 Service Unavailable"):
            get_weather.invoke({"location": "上海"})
