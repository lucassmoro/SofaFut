from src.models.lineup import Lineup
from src.models.player_fantasy import PlayerFantasy


class LineupBuilder:

    def __init__(self):
        self.__rodada = None
        self.__jogadores = []

    def com_rodada(self, rodada: int):
        self.__rodada = rodada
        return self

    def com_jogadores(self, jogadores: list[PlayerFantasy]):
        self.__jogadores = jogadores
        return self

    def build(self):
        if len(self.__jogadores) != 11:
            raise Exception("QUANTIDADE INCORRETA DE JOGADORES")

        quantidade_capitaes = 0
        for jogador in self.__jogadores:
            if jogador.capitao:
                quantidade_capitaes += 1

        if quantidade_capitaes != 1:
            raise Exception("QUANTIDADE DE CAPITAO INCORRETA")

        return Lineup(rodada=self.__rodada, jogadores=self.__jogadores)
