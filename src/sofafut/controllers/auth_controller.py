from sofafut.services.auth_service import AuthService, AuthUser


class AuthController:
    def __init__(self, auth_service: AuthService | None = None) -> None:
        self.auth_service = auth_service or AuthService()

    def cadastrar(self, username: str, senha: str) -> AuthUser:
        return self.auth_service.cadastrar(username, senha)

    def login(self, username: str, senha: str) -> AuthUser:
        return self.auth_service.login(username, senha)
