import logging
import sys
import warnings
from pathlib import Path

from sofafut.infrastructure.settings import PROJECT_ROOT


LOG_PATH = PROJECT_ROOT / "logs" / "sofafut.log"


def configure_logging(log_path: Path = LOG_PATH) -> Path:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
        ],
        force=True,
    )
    logging.captureWarnings(True)
    warnings.simplefilter("default")
    sys.excepthook = _log_uncaught_exception
    return log_path


def _log_uncaught_exception(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.getLogger("sofafut").critical(
        "Excecao nao tratada",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
