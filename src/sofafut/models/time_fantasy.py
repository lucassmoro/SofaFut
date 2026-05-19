from dataclasses import dataclass, field

from sofafut.models.base import Entity
from sofafut.models.favorito import Favorito
from sofafut.models.jogador import Jogador
from sofafut.models.pontuacao import PontuacaoRodada
from sofafut.models.transacao import TransacaoMercado


@dataclass
class TimeFantasy(Entity):
    usuario_id: str = ""
    nome: str = ""
    patrimonio: float = 100.0
    pontuacao_total: float = 0.0
    elenco: list[Jogador] = field(default_factory=list)
    favoritos: list[Favorito] = field(default_factory=list)
    transacoes: list[TransacaoMercado] = field(default_factory=list)
    pontuacoes: list[PontuacaoRodada] = field(default_factory=list)
