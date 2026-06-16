import json
from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from pathlib import Path
from secrets import token_hex

from sofafut.infrastructure.settings import PROJECT_ROOT


@dataclass(frozen=True)
class AuthUser:
    username: str


class AuthService:
    def __init__(self, users_path: Path | None = None) -> None:
        self.users_path = users_path or PROJECT_ROOT / "data" / "users.json"

    def cadastrar(self, username: str, senha: str, email: str = "", nome: str = "") -> AuthUser:
        username = self._normalizar_username(username)
        if not senha:
            raise ValueError("Informe a senha.")

        data = self._read_users()
        if username in data["users"]:
            raise ValueError("Usuario ja existe.")

        data["users"][username] = {
            "password_hash": self._hash_password(senha),
            "email": email.strip(),
            "nome": nome.strip() or username,
        }
        self._write_users(data)
        return AuthUser(username=username)

    def login(self, username: str, senha: str) -> AuthUser:
        username = self._normalizar_username(username)
        if not senha:
            raise ValueError("Informe a senha.")

        data = self._read_users()
        user_data = data["users"].get(username)
        if not user_data or not self._verify_password(senha, user_data["password_hash"]):
            raise ValueError("Usuario ou senha invalidos.")

        return AuthUser(username=username)

    def perfil(self, username: str) -> dict[str, str]:
        username = self._normalizar_username(username)
        data = self._read_users()
        user_data = data["users"].get(username)
        if user_data is None:
            raise ValueError("Usuario nao encontrado.")

        return {
            "username": username,
            "nome": user_data.get("nome", username),
            "email": user_data.get("email", ""),
        }

    def atualizar_perfil(
        self,
        username: str,
        nome: str | None = None,
        email: str | None = None,
        novo_username: str | None = None,
    ) -> AuthUser:
        username = self._normalizar_username(username)
        data = self._read_users()
        user_data = data["users"].get(username)
        if user_data is None:
            raise ValueError("Usuario nao encontrado.")

        target_username = self._normalizar_username(novo_username) if novo_username else username
        if target_username != username and target_username in data["users"]:
            raise ValueError("Usuario ja existe.")

        if nome is not None:
            user_data["nome"] = nome.strip()
        if email is not None:
            user_data["email"] = email.strip()

        if target_username != username:
            data["users"].pop(username)
            data["users"][target_username] = user_data

        self._write_users(data)
        return AuthUser(username=target_username)

    def _normalizar_username(self, username: str) -> str:
        username = username.strip()
        if not username:
            raise ValueError("Informe o usuario.")
        return username

    def _read_users(self) -> dict[str, dict[str, dict[str, str]]]:
        if not self.users_path.exists():
            return {"users": {}}

        with self.users_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if "users" not in data or not isinstance(data["users"], dict):
            raise ValueError("Arquivo de usuarios invalido.")
        return data

    def _write_users(self, data: dict[str, dict[str, dict[str, str]]]) -> None:
        self.users_path.parent.mkdir(parents=True, exist_ok=True)
        with self.users_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def _hash_password(self, senha: str) -> str:
        salt = token_hex(16)
        digest = pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return f"pbkdf2_sha256${salt}${digest.hex()}"

    def _verify_password(self, senha: str, senha_hash: str) -> bool:
        try:
            algoritmo, salt, digest = senha_hash.split("$")
        except ValueError:
            return False

        if algoritmo != "pbkdf2_sha256":
            return False

        novo_digest = pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return compare_digest(novo_digest.hex(), digest)
