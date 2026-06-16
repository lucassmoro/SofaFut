from sofafut.models.time_fantasy import TimeFantasy
from sofafut.services.ranking_service import RankingService


class RankingController:
    def __init__(self, ranking_service: RankingService) -> None:
        self.ranking_service = ranking_service

    def ranking(self) -> list[TimeFantasy]:
        return self.ranking_service.ranking()

    def historico_evolucao(self, usuario_id: str) -> list[dict[str, float | int]]:
        return self.ranking_service.historico_evolucao(usuario_id)
