import sys

from app.multi_agent import run_multi_agent
from app.observability import configure_logging


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python run_multi_agent.py "Your travel request"')
    configure_logging()
    print(run_multi_agent(sys.argv[1]))


if __name__ == "__main__":
    main()
