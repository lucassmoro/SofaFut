from sofafut.models.time_fantasy import TimeFantasy
from sofafut.repositories.memory_repository import MemoryRepository


class RankingService:
    def __init__(self, times: MemoryRepository) -> None:
        self.times = times

    def ranking(self) -> list[TimeFantasy]:
        times = [time for time in self.times.list() if isinstance(time, TimeFantasy)]
        return sorted(times, key=lambda time: (time.pontuacao_total, time.patrimonio), reverse=True)
