from dataclasses import dataclass

from sofafut.models.base import Entity


@dataclass
class EstatisticaJogador(Entity):
    jogador_id: str = ""
    partida_id: str = ""
    atuou: bool = False
    minutos: int = 0
    gols: int = 0
    assistencias: int = 0
    passes: int = 0
    precisao_passes: float = 0.0
    desarmes: int = 0
    finalizacoes: int = 0
    faltas: int = 0
    cartoes_amarelos: int = 0
    cartoes_vermelhos: int = 0
