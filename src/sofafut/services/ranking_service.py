from sofafut.models.time_fantasy import TimeFantasy
from sofafut.repositories.memory_repository import MemoryRepository


class RankingService:
    def __init__(self, times: MemoryRepository) -> None:
        self.times = times

    def ranking(self) -> list[TimeFantasy]:
        times = [time for time in self.times.list() if isinstance(time, TimeFantasy)]
        return sorted(times, key=lambda time: (time.pontuacao_total, time.patrimonio), reverse=True)

    def historico_evolucao(self, usuario_id: str) -> list[dict[str, float | int]]:
        time = self.times.find_one(lambda item: getattr(item, "usuario_id", None) == usuario_id)
        if not isinstance(time, TimeFantasy):
            raise ValueError("Time fantasy nao encontrado.")

        return [
            {
                "rodada": pontuacao.rodada,
                "pontos": pontuacao.pontos,
                "patrimonio": pontuacao.patrimonio_apos,
            }
            for pontuacao in sorted(time.pontuacoes, key=lambda item: item.rodada)
        ]
