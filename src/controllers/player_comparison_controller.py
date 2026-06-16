from src.controllers.app_controller import AppController


class PlayerComparisonController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller

    def comparar(self, jogador_a, jogador_b):
        return self.app_controller.comparar_jogadores(jogador_a, jogador_b)

    def estatisticas_jogador(self, jogador):
        return self.app_controller.estatisticas_jogador(jogador)
