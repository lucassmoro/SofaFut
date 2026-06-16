from src.controllers.app_controller import AppController


class UserProfileController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller

    def alterar_email(self, username, novo_email):
        return self.app_controller.alterar_email(username, novo_email)

    def alterar_nome(self, username, novo_username):
        return self.app_controller.alterar_nome(username, novo_username)

    def alterar_senha(self, username, senha_atual, nova_senha):
        return self.app_controller.alterar_senha(username, senha_atual, nova_senha)

    def usuario_logado(self):
        return self.app_controller.usuario_logado()
