import logging
from pathlib import Path


LOGGER_NAME = "travel_multi_agent"
DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "output" / "logs" / "travel-agent.log"


def configure_logging(log_path: Path = DEFAULT_LOG_PATH) -> logging.Logger:
    """Configure one local UTF-8 file logger without duplicating handlers."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
