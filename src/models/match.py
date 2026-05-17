from src.models.player_match import MatchPlayerStats

class Match:

    def __init__(self, mandante, visitante, data, jogadores_partida : list[MatchPlayerStats]):
        self.__mandante = mandante
        self.__visitante = visitante
        self.__data = data
        self.__jogadores_partida = jogadores_partida