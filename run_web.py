from app.observability import configure_logging
from app.tracing import configure_langsmith
from app.web import create_app


if __name__ == "__main__":
    configure_logging()
    configure_langsmith()
    create_app().run(host="127.0.0.1", port=5000, debug=False)
