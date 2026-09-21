from langchain_openai import ChatOpenAI

from app.config import load_settings


def ask_model(message: str, model_name: str = "deepseek-flash") -> str:
    """Send one user message to the configured chat model and return its text."""
    settings = load_settings()
    model = ChatOpenAI(
        model=model_name,
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com",
    )
    response = model.invoke(message)
    return str(response.content)
