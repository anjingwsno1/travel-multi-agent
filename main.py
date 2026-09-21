import sys

from app.model import ask_model


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python main.py "Your travel question"')
    print(ask_model(sys.argv[1]))


if __name__ == "__main__":
    main()

