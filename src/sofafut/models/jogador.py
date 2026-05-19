from dataclasses import dataclass

from sofafut.models.base import Entity
from sofafut.models.clube import Clube


@dataclass
class Jogador(Entity):
    nome: str = ""
    nacionalidade: str = ""
    numero_camisa: int = 0
    valor_mercado: float = 0.0
    clube: Clube | None = None


@dataclass
class JogadorLinha(Jogador):
    posicao: str = ""


@dataclass
class Goleiro(Jogador):
    defesas: int = 0
    defesas_penalti: int = 0
    gols_sofridos: int = 0
