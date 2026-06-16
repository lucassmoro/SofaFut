from src.models.player import Player


class PlayerRepository:

    def __init__(self):
        self._jogadores = []
    
    def listar_jogadores(self):
        return self._jogadores

    def definir_jogadores(self, jogadores):
        self._jogadores = jogadores

    def _converter_para_players(self, dados):
        jogadores = []

        for jogador in dados:
            jogadores.append(
                Player(
                    nome=jogador["nome"],
                    time=jogador["time"],
                    posicao=jogador["posicao"],
                    idade=jogador["idade"],
                    api_id=jogador.get("api_id"),
                    nome_time=jogador.get("nome_time"),
                    valor_mercado=jogador.get("valor_mercado", 10.0),
                )
            )

        return jogadores
