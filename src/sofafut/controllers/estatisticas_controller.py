from sofafut.models.estatistica import EstatisticaJogador
from sofafut.models.pontuacao import PontuacaoRodada
from sofafut.services.estatistica_service import EstatisticaService


class EstatisticasController:
    def __init__(self, estatistica_service: EstatisticaService) -> None:
        self.estatistica_service = estatistica_service

    def calcular_pontuacao(
        self,
        escalacao_id: str,
        estatisticas: list[EstatisticaJogador],
    ) -> PontuacaoRodada:
        return self.estatistica_service.calcular_pontuacao(escalacao_id, estatisticas)

    def verificar_atuacao(self, jogador_id: str, estatisticas: list[EstatisticaJogador]) -> bool:
        return self.estatistica_service.verificar_atuacao(jogador_id, estatisticas)

    def filtrar_atletas(
        self,
        estatisticas: list[EstatisticaJogador],
        criterio: str,
        minimo: float | int | None = None,
    ) -> list[EstatisticaJogador]:
        return self.estatistica_service.filtrar_atletas(estatisticas, criterio, minimo)

    def comparar_atletas(
        self,
        jogador_a_id: str,
        jogador_b_id: str,
        estatisticas: list[EstatisticaJogador],
    ) -> dict[str, dict[str, float | int | bool | str]]:
        return self.estatistica_service.comparar_atletas(jogador_a_id, jogador_b_id, estatisticas)
