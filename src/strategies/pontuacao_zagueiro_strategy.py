from src.strategies.pontuacao_padrao_strategy import PontuacaoPadraoStrategy


class PontuacaoZagueiroStrategy(PontuacaoPadraoStrategy):

    pontos_por_falta = 1
    desconto_por_gol_sofrido = 15
    bonus_sem_sofrer_gol = 20
