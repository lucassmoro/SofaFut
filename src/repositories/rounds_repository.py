class RoundRepository:

    def __init__(self):
        self.__rodadas = []

    def adicionar_rodada(self, rodada):
        self.__rodadas.append(rodada)

    def listar_rodadas(self):
        return self.__rodadas

    def buscar_por_numero(self, numero):
        for rodada in self.__rodadas:
            if rodada.numero == numero:
                return rodada
        return None