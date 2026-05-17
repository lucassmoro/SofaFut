from src.models.club import Club

class Player:

    def __init__(self, nome, time : Club, posicao, idade, gols, 
                 assistencias, cartoes_amarelos, cartoes_vermelhos, faltas, gols_sofridos):
        
        self.__nome = nome
        self.__time = time
        self.__posicao = posicao
        self.__idade = idade
        self.__gols = gols
        self.__assistencias = assistencias
        self.__cartoes_amarelos = cartoes_amarelos
        self.__cartoes_vermelhos = cartoes_vermelhos
        self.__faltas = faltas
        self.__gols_sofridos = gols_sofridos

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, nome):
        self.__nome = nome

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, time):
        self.__time = time

    @property
    def posicao(self):
        return self.__posicao

    @posicao.setter
    def posicao(self, posicao):
        self.__posicao = posicao

    @property
    def idade(self):
        return self.__idade

    @idade.setter
    def idade(self, idade):
        self.__idade = idade

    @property
    def gols(self):
        return self.__gols

    @gols.setter
    def gols(self, gols):
        self.__gols = gols

    @property
    def assistencias(self):
        return self.__assistencias

    @assistencias.setter
    def assistencias(self, assistencias):
        self.__assistencias = assistencias

    @property
    def cartoes_amarelos(self):
        return self.__cartoes_amarelos

    @cartoes_amarelos.setter
    def cartoes_amarelos(self, cartoes_amarelos):
        self.__cartoes_amarelos = cartoes_amarelos

    @property
    def cartoes_vermelhos(self):
        return self.__cartoes_vermelhos

    @cartoes_vermelhos.setter
    def cartoes_vermelhos(self, cartoes_vermelhos):
        self.__cartoes_vermelhos = cartoes_vermelhos

    @property
    def faltas(self):
        return self.__faltas

    @faltas.setter
    def faltas(self, faltas):
        self.__faltas = faltas

    @property
    def gols_sofridos(self):
        return self.__gols_sofridos

    @gols_sofridos.setter
    def gols_sofridos(self, gols_sofridos):
        self.__gols_sofridos = gols_sofridos