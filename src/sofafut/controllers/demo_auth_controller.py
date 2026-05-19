from sofafut.models.usuario import Usuario
from sofafut.services.demo_auth_service import DemoAuthService


class DemoAuthController:
    def __init__(self, auth_service: DemoAuthService) -> None:
        self.auth_service = auth_service

    def registrar(self, nome: str, email: str, senha: str) -> Usuario:
        return self.auth_service.registrar(nome, email, senha)

    def login(self, email: str, senha: str) -> Usuario:
        return self.auth_service.autenticar(email, senha)
