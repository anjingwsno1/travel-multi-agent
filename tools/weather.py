import json

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.config import load_weather_api_key


class WeatherInput(BaseModel):
    location: str = Field(description="要查询天气的城市或地点名称。")


@tool("get_weather", args_schema=WeatherInput)
def get_weather(location: str) -> str:
    """获取指定城市的当前天气。"""
    weather_api_key = load_weather_api_key()
    response = requests.get(
        "https://api.weatherapi.com/v1/current.json",
        params={"key": weather_api_key, "q": location, "aqi": "no", "alerts": "no"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return json.dumps(
        {
            "location": data["location"]["name"],
            "country": data["location"]["country"],
            "condition": data["current"]["condition"]["text"],
            "temperature_c": data["current"]["temp_c"],
            "feelslike_c": data["current"]["feelslike_c"],
        },
        ensure_ascii=False,
    )
