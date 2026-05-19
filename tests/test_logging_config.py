import logging
import tempfile
import unittest
import warnings
from pathlib import Path

from sofafut.infrastructure.logging_config import configure_logging


class LoggingConfigTest(unittest.TestCase):
    def test_logging_sobrescreve_arquivo_e_captura_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "sofafut.log"
            log_path.write_text("conteudo antigo", encoding="utf-8")

            configure_logging(log_path)
            logging.getLogger("teste").warning("aviso de log")
            warnings.warn("aviso python", UserWarning, stacklevel=1)

            content = log_path.read_text(encoding="utf-8")

            self.assertNotIn("conteudo antigo", content)
            self.assertIn("aviso de log", content)
            self.assertIn("aviso python", content)


if __name__ == "__main__":
    unittest.main()
