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
        if any(pontuacao.rodada == escalacao.rodada for pontuacao in time.pontuacoes):
            raise ValueError("Pontuacao da rodada ja calculada para este time.")
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

    def verificar_atuacao(self, jogador_id: str, estatisticas: list[EstatisticaJogador]) -> bool:
        estatistica = next((item for item in estatisticas if item.jogador_id == jogador_id), None)
        return bool(estatistica and estatistica.atuou)

    def filtrar_atletas(
        self,
        estatisticas: list[EstatisticaJogador],
        criterio: str,
        minimo: float | int | None = None,
        reverse: bool = True,
    ) -> list[EstatisticaJogador]:
        atributo = self._normalizar_criterio(criterio)
        filtradas = [
            estatistica
            for estatistica in estatisticas
            if hasattr(estatistica, atributo)
            and (minimo is None or float(getattr(estatistica, atributo) or 0) >= float(minimo))
        ]
        return sorted(filtradas, key=lambda item: float(getattr(item, atributo) or 0), reverse=reverse)

    def comparar_atletas(
        self,
        jogador_a_id: str,
        jogador_b_id: str,
        estatisticas: list[EstatisticaJogador],
    ) -> dict[str, dict[str, float | int | bool | str]]:
        estatistica_a = self._estatistica_por_jogador(jogador_a_id, estatisticas)
        estatistica_b = self._estatistica_por_jogador(jogador_b_id, estatisticas)
        campos = [
            "atuou",
            "minutos",
            "gols",
            "assistencias",
            "passes",
            "precisao_passes",
            "desarmes",
            "finalizacoes",
            "faltas",
            "cartoes_amarelos",
            "cartoes_vermelhos",
        ]
        return {
            campo: {
                jogador_a_id: getattr(estatistica_a, campo),
                jogador_b_id: getattr(estatistica_b, campo),
            }
            for campo in campos
        }

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

    def _normalizar_criterio(self, criterio: str) -> str:
        criterio = criterio.strip().casefold().replace(" ", "_")
        aliases = {
            "gol": "gols",
            "assistencia": "assistencias",
            "assistência": "assistencias",
            "cartao_amarelo": "cartoes_amarelos",
            "cartão_amarelo": "cartoes_amarelos",
            "cartao_vermelho": "cartoes_vermelhos",
            "cartão_vermelho": "cartoes_vermelhos",
            "precisao": "precisao_passes",
            "precisão": "precisao_passes",
        }
        return aliases.get(criterio, criterio)

    def _estatistica_por_jogador(
        self,
        jogador_id: str,
        estatisticas: list[EstatisticaJogador],
    ) -> EstatisticaJogador:
        estatistica = next((item for item in estatisticas if item.jogador_id == jogador_id), None)
        if estatistica is None:
            raise ValueError(f"Estatistica nao encontrada para jogador {jogador_id}.")
        return estatistica

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
