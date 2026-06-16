from sofafut.models.jogador import Jogador
from sofafut.models.time_fantasy import TimeFantasy
from sofafut.services.mercado_service import MercadoService


class MercadoController:
    def __init__(self, mercado_service: MercadoService) -> None:
        self.mercado_service = mercado_service

    def comprar(self, usuario_id: str, jogador: Jogador) -> TimeFantasy:
        return self.mercado_service.comprar(usuario_id, jogador)

    def vender(self, usuario_id: str, jogador_id: str) -> TimeFantasy:
        return self.mercado_service.vender(usuario_id, jogador_id)

    def fechar_mercado(self) -> None:
        self.mercado_service.fechar_mercado()

    def abrir_mercado(self) -> None:
        self.mercado_service.abrir_mercado()

    def elenco(self, usuario_id: str) -> list[Jogador]:
        return self.mercado_service.elenco(usuario_id)
