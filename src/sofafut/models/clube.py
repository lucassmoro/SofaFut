from dataclasses import dataclass

from sofafut.models.base import Entity


@dataclass
class Clube(Entity):
    nome: str = ""
    cidade: str = ""
    estadio: str = ""
    tecnico: str = ""
    vitorias: int = 0
    empates: int = 0
    derrotas: int = 0
