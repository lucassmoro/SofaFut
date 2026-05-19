import json
import tempfile
import unittest
from pathlib import Path

from sofafut.services.auth_service import AuthService


class AuthServiceTest(unittest.TestCase):
    def test_cadastro_guarda_hash_e_login_funciona(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            users_path = Path(temp_dir) / "users.json"
            service = AuthService(users_path)

            service.cadastrar("vini", "123456")
            user = service.login("vini", "123456")

            data = json.loads(users_path.read_text(encoding="utf-8"))
            password_hash = data["users"]["vini"]["password_hash"]

            self.assertEqual(user.username, "vini")
            self.assertNotEqual(password_hash, "123456")
            self.assertTrue(password_hash.startswith("pbkdf2_sha256$"))

    def test_cadastro_usuario_repetido_falha(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = AuthService(Path(temp_dir) / "users.json")

            service.cadastrar("vini", "123456")

            with self.assertRaisesRegex(ValueError, "Usuario ja existe"):
                service.cadastrar("vini", "abcdef")

    def test_login_invalido_falha(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = AuthService(Path(temp_dir) / "users.json")
            service.cadastrar("vini", "123456")

            with self.assertRaisesRegex(ValueError, "Usuario ou senha invalidos"):
                service.login("vini", "errada")


if __name__ == "__main__":
    unittest.main()
