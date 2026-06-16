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
        if jogador.id in {item.jogador.id for item in escalacao.jogadores if item.jogador is not None}:
            raise ValueError("Jogador ja escalado.")
        if capitao and escalacao.capitao() is not None:
            raise ValueError("A escalacao ja possui capitao.")

        escalacao.jogadores.append(
            JogadorEscalacao(jogador=jogador, posicao=posicao, titular=titular, capitao=capitao)
        )
        return escalacao

    def escolher_capitao(self, escalacao_id: str, jogador_id: str) -> Escalacao:
        escalacao = self._get_escalacao(escalacao_id)
        if escalacao.bloqueada:
            raise ValueError("Escalacao bloqueada.")

        escolhido = None
        for jogador_escalado in escalacao.jogadores:
            jogador_escalado.capitao = False
            if jogador_escalado.jogador and jogador_escalado.jogador.id == jogador_id:
                escolhido = jogador_escalado

        if escolhido is None:
            raise ValueError("Jogador nao esta na escalacao.")

        escolhido.capitao = True
        return escalacao

    def bloquear(self, escalacao_id: str) -> Escalacao:
        escalacao = self._get_escalacao(escalacao_id)
        if escalacao.capitao() is None:
            raise ValueError("Escolha um capitao antes de bloquear a escalacao.")
        esperados = self._quantidade_jogadores_formacao(escalacao.formacao)
        if len(escalacao.jogadores) != esperados:
            raise ValueError(
                f"Escalacao incompleta: a formacao {escalacao.formacao} exige {esperados} jogadores."
            )
        escalacao.bloqueada = True
        return escalacao

    def _quantidade_jogadores_formacao(self, formacao: str) -> int:
        partes = [parte.strip() for parte in formacao.split("-") if parte.strip()]
        if not partes:
            raise ValueError("Formacao invalida.")

        try:
            jogadores_linha = sum(int(parte) for parte in partes)
        except ValueError as exc:
            raise ValueError("Formacao invalida.") from exc

        return jogadores_linha + 1

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
