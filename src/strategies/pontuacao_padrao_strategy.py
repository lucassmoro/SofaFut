from src.models.player_match import MatchPlayerStats
from src.strategies.pontuacao_strategy import PontuacaoStrategy


class PontuacaoPadraoStrategy(PontuacaoStrategy):

    pontos_por_gol = 40
    pontos_por_assistencia = 20
    pontos_por_falta = 3
    desconto_por_gol_sofrido = 10
    bonus_sem_sofrer_gol = 0

    def calcular(self, jogador: MatchPlayerStats, capitao: bool):
        pontuacao = 0

        if jogador.atuou:
            pontuacao += jogador.gols * self.pontos_por_gol
            pontuacao += jogador.assistencias * self.pontos_por_assistencia
            pontuacao -= jogador.cartoes_amarelos * 10
            pontuacao -= jogador.cartoes_vermelhos * 50
            pontuacao += jogador.faltas * self.pontos_por_falta
            pontuacao -= jogador.gols_sofridos * self.desconto_por_gol_sofrido

            if jogador.gols_sofridos == 0:
                pontuacao += self.bonus_sem_sofrer_gol

        if capitao:
            pontuacao *= 2

        return pontuacao
