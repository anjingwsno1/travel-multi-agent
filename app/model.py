from langchain_openai import ChatOpenAI

from app.config import load_settings


def create_chat_model(model_name: str = "deepseek-flash") -> ChatOpenAI:
    """Create the DeepSeek-compatible chat model used by the application."""
    settings = load_settings()
    return ChatOpenAI(
        model=model_name,
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com",
    )


def ask_model(message: str, model_name: str = "deepseek-flash") -> str:
    """Send one user message to the configured chat model and return its text."""
    model = create_chat_model(model_name)
    response = model.invoke(message)
    return str(response.content)
