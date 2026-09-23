import sys

from app.model import ask_model
from app.observability import configure_logging
from app.tracing import configure_langsmith


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python main.py "Your travel question"')
    configure_logging()
    configure_langsmith()
    print(ask_model(sys.argv[1]))


if __name__ == "__main__":
    main()
