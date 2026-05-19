from dataclasses import dataclass

from sofafut.models.base import Entity


@dataclass
class PontuacaoRodada(Entity):
    time_fantasy_id: str = ""
    rodada: int = 0
    pontos: float = 0.0
    patrimonio_apos: float = 0.0
