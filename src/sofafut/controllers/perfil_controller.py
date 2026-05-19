from sofafut.models.usuario import Usuario
from sofafut.services.demo_auth_service import DemoAuthService


class PerfilController:
    def __init__(self, auth_service: DemoAuthService) -> None:
        self.auth_service = auth_service

    def atualizar(self, usuario_id: str, nome: str | None = None, email: str | None = None) -> Usuario:
        return self.auth_service.atualizar_perfil(usuario_id, nome, email)
