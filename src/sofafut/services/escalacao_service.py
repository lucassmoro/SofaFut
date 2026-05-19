from sofafut.models.escalacao import Escalacao, JogadorEscalacao
from sofafut.models.jogador import Jogador
from sofafut.models.time_fantasy import TimeFantasy
from sofafut.repositories.memory_repository import MemoryRepository


class EscalacaoService:
    def __init__(self, escalacoes: MemoryRepository, times: MemoryRepository) -> None:
        self.escalacoes = escalacoes
        self.times = times

    def criar_escalacao(self, usuario_id: str, rodada: int, formacao: str) -> Escalacao:
        time = self._get_time_by_usuario(usuario_id)
        escalacao = Escalacao(time_fantasy_id=time.id, rodada=rodada, formacao=formacao)
        self.escalacoes.add(escalacao)
        return escalacao

    def escalar_jogador(
        self,
        escalacao_id: str,
        jogador: Jogador,
        posicao: str,
        titular: bool = True,
        capitao: bool = False,
    ) -> Escalacao:
        escalacao = self._get_escalacao(escalacao_id)
        if escalacao.bloqueada:
            raise ValueError("Escalacao bloqueada.")
        if capitao and escalacao.capitao() is not None:
            raise ValueError("A escalacao ja possui capitao.")

        escalacao.jogadores.append(
            JogadorEscalacao(jogador=jogador, posicao=posicao, titular=titular, capitao=capitao)
        )
        return escalacao

    def bloquear(self, escalacao_id: str) -> Escalacao:
        escalacao = self._get_escalacao(escalacao_id)
        if escalacao.capitao() is None:
            raise ValueError("Escolha um capitao antes de bloquear a escalacao.")
        escalacao.bloqueada = True
        return escalacao

    def _get_escalacao(self, escalacao_id: str) -> Escalacao:
        escalacao = self.escalacoes.get(escalacao_id)
        if not isinstance(escalacao, Escalacao):
            raise ValueError("Escalacao invalida.")
        return escalacao

    def _get_time_by_usuario(self, usuario_id: str) -> TimeFantasy:
        time = self.times.find_one(lambda item: getattr(item, "usuario_id", None) == usuario_id)
        if not isinstance(time, TimeFantasy):
            raise ValueError("Time fantasy nao encontrado.")
        return time
