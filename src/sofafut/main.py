from sofafut.app import SofaFutApp
from sofafut.infrastructure.logging_config import configure_logging


def main() -> None:
    configure_logging()
    app = SofaFutApp()
    raise SystemExit(app.run())


if __name__ == "__main__":
    main()
