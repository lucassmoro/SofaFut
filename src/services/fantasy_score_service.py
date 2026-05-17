from src.models.match import Match
from src.models.rounds import Round
from src.models.lineup import Lineup
from src.models.player_match import MatchPlayerStats
from src.models.player_fantasy import PlayerFantasy
from src.models.player import Player
from src.repositories.rounds_repository import RoundRepository

class FantasyScoreService:

    def calcular_pontuacao_lineup(self, escalacao : Lineup, rodadas_repo : RoundRepository):
        
        round = rodadas_repo.buscar_por_numero(escalacao.rodada)

        for partida in round.partidas:
            for jogador in partida.jogadores_partida:
                self.calculo_pontuacao_logica(jogador)

    def calculo_pontuacao_logica(self, jogador : MatchPlayerStats):
        pass