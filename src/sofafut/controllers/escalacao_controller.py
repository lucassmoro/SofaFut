from sofafut.models.escalacao import Escalacao
from sofafut.models.jogador import Jogador
from sofafut.services.escalacao_service import EscalacaoService


class EscalacaoController:
    def __init__(self, escalacao_service: EscalacaoService) -> None:
        self.escalacao_service = escalacao_service

    def criar_escalacao(self, usuario_id: str, rodada: int, formacao: str) -> Escalacao:
        return self.escalacao_service.criar_escalacao(usuario_id, rodada, formacao)

    def escalar_jogador(
        self,
        escalacao_id: str,
        jogador: Jogador,
        posicao: str,
        titular: bool = True,
        capitao: bool = False,
    ) -> Escalacao:
        return self.escalacao_service.escalar_jogador(escalacao_id, jogador, posicao, titular, capitao)

    def escolher_capitao(self, escalacao_id: str, jogador_id: str) -> Escalacao:
        return self.escalacao_service.escolher_capitao(escalacao_id, jogador_id)

    def bloquear(self, escalacao_id: str) -> Escalacao:
        return self.escalacao_service.bloquear(escalacao_id)
