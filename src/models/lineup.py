from player import Player
class Lineup():

    def __init__(self, rodada, jogadores : list[Player], capitao, pontuacao):

        self.__rodada = rodada
        self.__jogadores = jogadores
        self.__capitao = capitao
        self.__pontuacao = pontuacao

    @property
    def rodada(self):
        return self.__rodada

    @rodada.setter
    def rodada(self, rodada):
        self.__rodada = rodada

    @property
    def jogadores(self):
        return self.__jogadores

    @jogadores.setter
    def jogadores(self, jogadores):
        self.__jogadores = jogadores

    @property
    def capitao(self):
        return self.__capitao

    @capitao.setter
    def capitao(self, capitao):
        self.__capitao = capitao

    @property
    def pontuacao(self):
        return self.__pontuacao

    @pontuacao.setter
    def pontuacao(self, pontuacao):
        self.__pontuacao = pontuacao