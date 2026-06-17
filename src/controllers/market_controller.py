from src.controllers.app_controller import AppController


class MarketController:
    def __init__(self, app_controller: AppController):
        self.app_controller = app_controller

    def comprar(self, username, jogador):
        return self.app_controller.comprar_jogador(username, jogador)

    def vender(self, username, jogador):
        return self.app_controller.vender_jogador(username, jogador)

    def limpar_elenco_rodada(self, username):
        return self.app_controller.limpar_elenco_rodada(username)

    def listar_elenco(self, username):
        return self.app_controller.listar_elenco(username)

    def listar_transacoes(self, username):
        return self.app_controller.listar_transacoes_mercado(username)

    def patrimonio(self, username):
        return self.app_controller.patrimonio_time_fantasy(username)

    def historico_patrimonio(self, username):
        return self.app_controller.historico_patrimonio(username)

    def mercado_esta_aberto(self):
        return self.app_controller.mercado_esta_aberto()

    def abrir_mercado(self):
        return self.app_controller.abrir_mercado()

    def fechar_mercado(self):
        return self.app_controller.fechar_mercado()
