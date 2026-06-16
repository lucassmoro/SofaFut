from sofafut.services.auth_service import AuthService, AuthUser


class AuthController:
    def __init__(self, auth_service: AuthService | None = None) -> None:
        self.auth_service = auth_service or AuthService()

    def cadastrar(self, username: str, senha: str, email: str = "", nome: str = "") -> AuthUser:
        return self.auth_service.cadastrar(username, senha, email=email, nome=nome)

    def login(self, username: str, senha: str) -> AuthUser:
        return self.auth_service.login(username, senha)

    def perfil(self, username: str) -> dict[str, str]:
        return self.auth_service.perfil(username)

    def atualizar_perfil(
        self,
        username: str,
        nome: str | None = None,
        email: str | None = None,
        novo_username: str | None = None,
    ) -> AuthUser:
        return self.auth_service.atualizar_perfil(username, nome, email, novo_username)
