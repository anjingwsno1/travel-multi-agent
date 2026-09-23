import os

from dotenv import load_dotenv

from app.config import PROJECT_ROOT
from app.observability import get_logger


def configure_langsmith() -> bool:
    """Enable LangSmith tracing when a project-local API key is available."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("LANGSMITH_API_KEY")
    tracing_enabled = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    if not api_key or not tracing_enabled:
        get_logger().info("event=langsmith.disabled")
        return False

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = api_key
    os.environ.setdefault("LANGSMITH_PROJECT", "travel-multi-agent")
    get_logger().info("event=langsmith.enabled project=%s", os.environ["LANGSMITH_PROJECT"])
    return True
