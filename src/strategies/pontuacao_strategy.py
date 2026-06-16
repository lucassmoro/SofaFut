from abc import ABC, abstractmethod

from src.models.player_match import MatchPlayerStats


class PontuacaoStrategy(ABC):

    @abstractmethod
    def calcular(self, jogador: MatchPlayerStats, capitao: bool):
        pass
