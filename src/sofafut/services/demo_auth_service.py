from hashlib import pbkdf2_hmac
from secrets import token_hex

from sofafut.models.time_fantasy import TimeFantasy
from sofafut.models.usuario import Usuario
from sofafut.repositories.memory_repository import MemoryRepository


class DemoAuthService:
    def __init__(self, usuarios: MemoryRepository, times: MemoryRepository) -> None:
        self.usuarios = usuarios
        self.times = times

    def registrar(self, nome: str, email: str, senha: str) -> Usuario:
        existente = self.usuarios.find_one(lambda usuario: getattr(usuario, "email", None) == email)
        if existente:
            raise ValueError("Email ja cadastrado.")

        usuario = Usuario(nome=nome, email=email, senha_hash=self._hash_password(senha))
        self.usuarios.add(usuario)
        self.times.add(TimeFantasy(usuario_id=usuario.id, nome=f"Time de {nome}"))
        return usuario

    def autenticar(self, email: str, senha: str) -> Usuario:
        usuario = self.usuarios.find_one(lambda item: getattr(item, "email", None) == email)
        if not isinstance(usuario, Usuario) or not self._verify_password(senha, usuario.senha_hash):
            raise ValueError("Credenciais invalidas.")
        return usuario

    def atualizar_perfil(self, usuario_id: str, nome: str | None = None, email: str | None = None) -> Usuario:
        usuario = self.usuarios.get(usuario_id)
        if not isinstance(usuario, Usuario):
            raise ValueError("Usuario invalido.")
        if nome:
            usuario.nome = nome
        if email:
            usuario.email = email
        return usuario

    def _hash_password(self, senha: str) -> str:
        salt = token_hex(16)
        digest = pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return f"pbkdf2_sha256${salt}${digest.hex()}"

    def _verify_password(self, senha: str, senha_hash: str) -> bool:
        algoritmo, salt, digest = senha_hash.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        novo_digest = pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return novo_digest.hex() == digest
