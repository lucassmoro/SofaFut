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
            for jogador in partida.jogadores_partida: # acessa os players_match
                for jogador_fantasy in escalacao.jogadores: # acesssa os player_fantasy
                    
                    if jogador_fantasy.jogador == jogador.jogador: # verifica se ambos player_ referenciam o mesmo jogador
                        escalacao.pontuacao += self.calculo_pontuacao_logica(jogador)

        return escalacao.pontuacao

    def calculo_pontuacao_logica(self, jogador : MatchPlayerStats):
        pontuacao = 0
        if jogador.atuou:

            pontuacao += jogador.gols * 40
            pontuacao += jogador.assistencias * 20
            pontuacao -= jogador.cartoes_amarelos * 10
            pontuacao -= jogador.cartoes_vermelhos * 50
            pontuacao += jogador.faltas * 3
            pontuacao -= jogador.gols_sofridos * 10

        return pontuacao