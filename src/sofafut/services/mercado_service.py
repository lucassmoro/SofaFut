from sofafut.models.jogador import Jogador
from sofafut.models.time_fantasy import TimeFantasy
from sofafut.models.transacao import TipoTransacao, TransacaoMercado
from sofafut.repositories.memory_repository import MemoryRepository


class MercadoService:
    def __init__(self, times: MemoryRepository) -> None:
        self.times = times
        self.mercado_aberto = True

    def comprar(self, usuario_id: str, jogador: Jogador) -> TimeFantasy:
        self._validar_mercado_aberto()
        time = self._get_time_by_usuario(usuario_id)
        if any(item.id == jogador.id for item in time.elenco):
            raise ValueError("Jogador ja pertence ao time.")
        if time.patrimonio < jogador.valor_mercado:
            raise ValueError("Saldo insuficiente para comprar jogador.")

        time.patrimonio -= jogador.valor_mercado
        time.elenco.append(jogador)
        time.transacoes.append(
            TransacaoMercado(
                time_fantasy_id=time.id,
                jogador_id=jogador.id,
                tipo=TipoTransacao.COMPRA,
                valor=jogador.valor_mercado,
            )
        )
        return time

    def vender(self, usuario_id: str, jogador_id: str) -> TimeFantasy:
        self._validar_mercado_aberto()
        time = self._get_time_by_usuario(usuario_id)
        jogador = next((item for item in time.elenco if item.id == jogador_id), None)
        if jogador is None:
            raise ValueError("Jogador nao pertence ao time.")

        time.elenco.remove(jogador)
        time.patrimonio += jogador.valor_mercado
        time.transacoes.append(
            TransacaoMercado(
                time_fantasy_id=time.id,
                jogador_id=jogador.id,
                tipo=TipoTransacao.VENDA,
                valor=jogador.valor_mercado,
            )
        )
        return time

    def fechar_mercado(self) -> None:
        self.mercado_aberto = False

    def abrir_mercado(self) -> None:
        self.mercado_aberto = True

    def elenco(self, usuario_id: str) -> list[Jogador]:
        return list(self._get_time_by_usuario(usuario_id).elenco)

    def transacoes(self, usuario_id: str) -> list[TransacaoMercado]:
        return list(self._get_time_by_usuario(usuario_id).transacoes)

    def _validar_mercado_aberto(self) -> None:
        if not self.mercado_aberto:
            raise ValueError("Mercado fechado para transacoes.")

    def _get_time_by_usuario(self, usuario_id: str) -> TimeFantasy:
        time = self.times.find_one(lambda item: getattr(item, "usuario_id", None) == usuario_id)
        if not isinstance(time, TimeFantasy):
            raise ValueError("Time fantasy nao encontrado.")
        return time
