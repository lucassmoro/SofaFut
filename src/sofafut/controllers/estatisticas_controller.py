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
