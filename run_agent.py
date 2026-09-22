import sys

from app.travel_agent import run_travel_agent


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python run_agent.py "Your travel question"')
    print(run_travel_agent(sys.argv[1]))


if __name__ == "__main__":
    main()
