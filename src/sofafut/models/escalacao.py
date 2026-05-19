from dataclasses import dataclass, field

from sofafut.models.base import Entity
from sofafut.models.jogador import Jogador


@dataclass
class JogadorEscalacao(Entity):
    jogador: Jogador | None = None
    posicao: str = ""
    titular: bool = True
    capitao: bool = False
    pontuacao: float = 0.0


@dataclass
class Escalacao(Entity):
    time_fantasy_id: str = ""
    rodada: int = 0
    formacao: str = ""
    bloqueada: bool = False
    jogadores: list[JogadorEscalacao] = field(default_factory=list)

    def capitao(self) -> JogadorEscalacao | None:
        return next((jogador for jogador in self.jogadores if jogador.capitao), None)
