from src.controllers.app_controller import AppController


class FavoriteController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller

    def favoritar_jogador(self, username, jogador):
        return self.app_controller.favoritar_jogador(username, jogador)

    def remover_jogador(self, username, jogador):
        return self.app_controller.remover_favorito_jogador(username, jogador)

    def listar_jogadores(self, username):
        return self.app_controller.listar_jogadores_favoritos(username)

    def favoritar_clube(self, username, nome_clube):
        return self.app_controller.favoritar_clube(username, nome_clube)

    def remover_clube(self, username, nome_clube):
        return self.app_controller.remover_favorito_clube(username, nome_clube)

    def listar_clubes(self, username):
        return self.app_controller.listar_clubes_favoritos(username)
