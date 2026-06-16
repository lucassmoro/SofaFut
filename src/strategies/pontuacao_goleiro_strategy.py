from src.strategies.pontuacao_zagueiro_strategy import PontuacaoZagueiroStrategy


class PontuacaoGoleiroStrategy(PontuacaoZagueiroStrategy):

    desconto_por_gol_sofrido = 20
    bonus_sem_sofrer_gol = 30
