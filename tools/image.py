import uuid
from pathlib import Path

import requests
from langchain_core.tools import tool
from openai import OpenAI
from pydantic import BaseModel, Field

from app.config import load_ark_api_key


ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
SEEDREAM_MODEL = "doubao-seedream-5-0-lite-260128"
IMAGE_DIRECTORY = Path(__file__).resolve().parent.parent / "images"


class GenerateImageInput(BaseModel):
    prompt: str = Field(description="用于生成旅行配图的详细文字描述。")


@tool("generate_image", args_schema=GenerateImageInput)
def generate_image(prompt: str) -> str:
    """使用豆包 Seedream 根据文字描述生成一张旅行配图，并返回本地文件路径。"""
    client = OpenAI(api_key=load_ark_api_key(), base_url=ARK_BASE_URL)
    result = client.images.generate(
        model=SEEDREAM_MODEL,
        prompt=prompt,
        size="1920x1920",
        response_format="url",
    )
    image_url = result.data[0].url
    if not image_url:
        raise RuntimeError("豆包图片服务未返回图片 URL。")

    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    IMAGE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    image_path = IMAGE_DIRECTORY / f"{uuid.uuid4()}.png"
    image_path.write_bytes(response.content)
    return str(image_path)
