from sofafut.models.escalacao import Escalacao
from sofafut.models.estatistica import EstatisticaJogador
from sofafut.models.pontuacao import PontuacaoRodada
from sofafut.models.time_fantasy import TimeFantasy
from sofafut.repositories.memory_repository import MemoryRepository


class EstatisticaService:
    def __init__(self, escalacoes: MemoryRepository, times: MemoryRepository) -> None:
        self.escalacoes = escalacoes
        self.times = times

    def calcular_pontuacao(self, escalacao_id: str, estatisticas: list[EstatisticaJogador]) -> PontuacaoRodada:
        escalacao = self._get_escalacao(escalacao_id)
        time = self._get_time(escalacao.time_fantasy_id)
        pontos = 0.0

        for jogador_escalado in escalacao.jogadores:
            estatistica = next(
                (item for item in estatisticas if jogador_escalado.jogador and item.jogador_id == jogador_escalado.jogador.id),
                None,
            )
            if estatistica is None or not estatistica.atuou:
                jogador_escalado.pontuacao = 0.0
                continue

            jogador_escalado.pontuacao = self._calcular_jogador(estatistica)
            if not jogador_escalado.titular:
                jogador_escalado.pontuacao *= 0.5
            if jogador_escalado.capitao:
                jogador_escalado.pontuacao *= 2
            pontos += jogador_escalado.pontuacao

        pontuacao = PontuacaoRodada(
            time_fantasy_id=time.id,
            rodada=escalacao.rodada,
            pontos=pontos,
            patrimonio_apos=time.patrimonio,
        )
        time.pontuacao_total += pontos
        time.pontuacoes.append(pontuacao)
        return pontuacao

    def _calcular_jogador(self, estatistica: EstatisticaJogador) -> float:
        return (
            estatistica.gols * 8
            + estatistica.assistencias * 5
            + estatistica.desarmes * 1.5
            + estatistica.finalizacoes * 0.8
            - estatistica.cartoes_amarelos * 1
            - estatistica.cartoes_vermelhos * 3
            - estatistica.faltas * 0.5
        )

    def _get_escalacao(self, escalacao_id: str) -> Escalacao:
        escalacao = self.escalacoes.get(escalacao_id)
        if not isinstance(escalacao, Escalacao):
            raise ValueError("Escalacao invalida.")
        return escalacao

    def _get_time(self, time_id: str) -> TimeFantasy:
        time = self.times.get(time_id)
        if not isinstance(time, TimeFantasy):
            raise ValueError("Time fantasy invalido.")
        return time
