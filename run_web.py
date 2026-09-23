from app.observability import configure_logging
from app.web import create_app


if __name__ == "__main__":
    configure_logging()
    create_app().run(host="127.0.0.1", port=5000, debug=False)
