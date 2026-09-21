import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    deepseek_api_key: str


def load_settings() -> Settings:
    """Load required runtime settings from the project-local .env file."""
    load_dotenv(PROJECT_ROOT / ".env")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required. Copy .env.example to .env and set it.")
    return Settings(deepseek_api_key=deepseek_api_key)


def load_weather_api_key() -> str:
    """Load the WeatherAPI key when the weather tool is used."""
    load_dotenv(PROJECT_ROOT / ".env")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    if not weather_api_key:
        raise RuntimeError("WEATHER_API_KEY is required. Copy .env.example to .env and set it.")
    return weather_api_key
