from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Usuario:
    nome: str
    email: str
    senha_hash: str
    id: UUID = field(default_factory=uuid4)
    ativo: bool = True
    criado_em: datetime = field(default_factory=datetime.now)