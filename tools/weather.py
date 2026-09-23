import json

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.observability import get_logger

class WeatherInput(BaseModel):
    location: str = Field(description="要查询天气的城市或地点名称。")


@tool("get_weather", args_schema=WeatherInput)
def get_weather(location: str) -> str:
    """获取指定城市的当前天气和未来三天预报。"""
    logger = get_logger()
    logger.info("event=tool.start tool=get_weather")
    geocoding_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1, "language": "zh", "format": "json"},
        timeout=10,
    )
    geocoding_response.raise_for_status()
    results = geocoding_response.json().get("results", [])
    if not results:
        logger.warning("event=tool.not_found tool=get_weather")
        raise ValueError(f"未找到地点：{location}")

    place = results[0]
    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,apparent_temperature,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "forecast_days": 3,
        },
        timeout=10,
    )
    weather_response.raise_for_status()
    data = weather_response.json()

    daily = data["daily"]
    forecast = [
        {
            "date": daily["time"][index],
            "condition": weather_code_to_text(daily["weather_code"][index]),
            "temperature_max_c": daily["temperature_2m_max"][index],
            "temperature_min_c": daily["temperature_2m_min"][index],
            "precipitation_probability_max": daily["precipitation_probability_max"][index],
        }
        for index in range(len(daily["time"]))
    ]

    result = json.dumps(
        {
            "location": place["name"],
            "country": place.get("country"),
            "current": {
                "condition": weather_code_to_text(data["current"]["weather_code"]),
                "temperature_c": data["current"]["temperature_2m"],
                "feelslike_c": data["current"]["apparent_temperature"],
            },
            "forecast": forecast,
        },
        ensure_ascii=False,
    )
    logger.info("event=tool.success tool=get_weather forecast_days=%d", len(forecast))
    return result


def weather_code_to_text(weather_code: int) -> str:
    if weather_code == 0:
        return "晴"
    if weather_code in {1, 2, 3}:
        return "多云"
    if weather_code in {45, 48}:
        return "雾"
    if weather_code in {51, 53, 55, 56, 57}:
        return "毛毛雨"
    if weather_code in {61, 63, 65, 66, 67, 80, 81, 82}:
        return "雨"
    if weather_code in {71, 73, 75, 77, 85, 86}:
        return "雪"
    if weather_code in {95, 96, 99}:
        return "雷暴"
    return "未知"
