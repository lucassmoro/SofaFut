from src.strategies.pontuacao_atacante_strategy import PontuacaoAtacanteStrategy
from src.strategies.pontuacao_goleiro_strategy import PontuacaoGoleiroStrategy
from src.strategies.pontuacao_meia_strategy import PontuacaoMeiaStrategy
from src.strategies.pontuacao_padrao_strategy import PontuacaoPadraoStrategy
from src.strategies.pontuacao_zagueiro_strategy import PontuacaoZagueiroStrategy


class PontuacaoStrategyFactory:

    def criar_por_posicao(self, posicao):
        posicao_normalizada = self.__normalizar_posicao(posicao)

        if posicao_normalizada in ["g", "goleiro", "goalkeeper"]:
            return PontuacaoGoleiroStrategy()

        if posicao_normalizada in ["d", "zagueiro", "defensor", "defender"]:
            return PontuacaoZagueiroStrategy()

        if posicao_normalizada in ["m", "meia", "meio-campo", "midfielder"]:
            return PontuacaoMeiaStrategy()

        if posicao_normalizada in ["f", "atacante", "forward", "attacker"]:
            return PontuacaoAtacanteStrategy()

        return PontuacaoPadraoStrategy()

    def __normalizar_posicao(self, posicao):
        return (posicao or "").casefold().strip()
