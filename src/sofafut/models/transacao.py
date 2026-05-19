from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from sofafut.models.base import Entity


class TipoTransacao(StrEnum):
    COMPRA = "compra"
    VENDA = "venda"


@dataclass
class TransacaoMercado(Entity):
    time_fantasy_id: str = ""
    jogador_id: str = ""
    tipo: TipoTransacao = TipoTransacao.COMPRA
    valor: float = 0.0
    data_hora: datetime = field(default_factory=datetime.now)
