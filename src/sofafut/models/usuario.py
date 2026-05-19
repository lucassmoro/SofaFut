from dataclasses import dataclass, field
from datetime import datetime

from sofafut.models.base import Entity


@dataclass
class Usuario(Entity):
    nome: str = ""
    email: str = ""
    senha_hash: str = ""
    data_cadastro: datetime = field(default_factory=datetime.now)
