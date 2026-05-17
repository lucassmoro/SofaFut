from src.models.match import Match

class Round:

    def __init__(self, numero, partidas : list[Match]):
        self.__numero = numero
        self.__partidas = partidas

    @property
    def numero(self):
        return self.__numero

    @numero.setter
    def numero(self, numero):
        self.__numero = numero

    @property
    def partidas(self):
        return self.__partidas

    @partidas.setter
    def partidas(self, partidas):
        self.__partidas = partidas