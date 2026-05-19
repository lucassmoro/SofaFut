from dataclasses import dataclass, field
from datetime import datetime

from sofafut.models.base import Entity


@dataclass
class Favorito(Entity):
    usuario_id: str = ""
    entidade_id: str = ""
    tipo_entidade: str = ""
    criado_em: datetime = field(default_factory=datetime.now)
