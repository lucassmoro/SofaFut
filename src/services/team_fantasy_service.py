from src.builders.lineup_builder import LineupBuilder
from src.models.match import Match
from src.models.rounds import Round
from src.models.lineup import Lineup
from src.models.player_match import MatchPlayerStats
from src.models.player_fantasy import PlayerFantasy
from src.models.player import Player
from src.repositories.rounds_repository import RoundRepository
from src.models.user import User
from src.models.team_fantasy import TeamFantasy
from src.strategies.pontuacao_strategy_factory import PontuacaoStrategyFactory

class TeamFantasyService:

    def __init__(self):
        self.pontuacao_strategy_factory = PontuacaoStrategyFactory()

    def calcular_pontuacao_lineup(self, escalacao : Lineup, rodadas_repo : RoundRepository):

        round = rodadas_repo.buscar_por_numero(escalacao.rodada)
        escalacao.pontuacao = 0

        for jogador_fantasy in escalacao.jogadores:
            jogador_fantasy.pontuacao = 0

        for partida in round.partidas:
            for jogador in partida.jogadores_partida: # acessa os players_match
                for jogador_fantasy in escalacao.jogadores: # acesssa os player_fantasy
                    
                    if jogador_fantasy.jogador == jogador.jogador: # verifica se ambos player_ referenciam o mesmo jogador
                        jogador_fantasy.pontuacao = self.calcular_pontuacao_jogador(jogador, jogador_fantasy.capitao)
                        escalacao.pontuacao += jogador_fantasy.pontuacao

        return escalacao.pontuacao

    def calcular_pontuacao_jogador(self, jogador : MatchPlayerStats, capitao : bool):
        strategy = self.pontuacao_strategy_factory.criar_por_posicao(jogador.jogador.posicao)
        return strategy.calcular(jogador, capitao)
    
    def montar_escalacao(self, user : User, rodada : int, jogadores : list[PlayerFantasy]):
        team = user.team_fantasy

        lineup = (
            LineupBuilder()
            .com_rodada(rodada)
            .com_jogadores(jogadores)
            .build()
        )

        team.escalacoes[rodada] = lineup

        return team.escalacoes[rodada]


    def executar_rodada(self, user : User, rodada : int, jogadores : list[PlayerFantasy], rodadas_repo : RoundRepository):
        
        # primeiro tem que fazer uma verificacao se a rodada ja existe, se ja existir vai estar em cache em algum arquivo json
        # e dai é so acessar o arquivo. Se nao estiver dai tem que ver se faz uma chamada de API pra verificar se esta disponivel

        pontuacao_anterior = 0
        lineup_anterior = user.team_fantasy.escalacoes.get(rodada)
        if lineup_anterior is not None:
            pontuacao_anterior = lineup_anterior.pontuacao or 0

        lineup = self.montar_escalacao(user, rodada, jogadores)
        pontuacao_rodada = self.calcular_pontuacao_lineup(lineup, rodadas_repo)

        user.pontuacao += pontuacao_rodada - pontuacao_anterior
        return pontuacao_rodada
        
