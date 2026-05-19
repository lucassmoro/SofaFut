from dataclasses import dataclass
from datetime import datetime

from sofafut.models.base import Entity
from sofafut.models.clube import Clube


@dataclass
class Partida(Entity):
    mandante: Clube | None = None
    visitante: Clube | None = None
    data_hora: datetime | None = None
    rodada: int = 0
    status: str = "agendada"
    gols_mandante: int = 0
    gols_visitante: int = 0
