from sofafut.demo_console_app import build_console_app
from sofafut.infrastructure.logging_config import configure_logging


def main() -> None:
    configure_logging()
    app = build_console_app()
    app.run_demo()


if __name__ == "__main__":
    main()
