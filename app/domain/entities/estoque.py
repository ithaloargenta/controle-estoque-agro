from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class Estoque:
    produto_id: UUID
    localizacao: str
    quantidade: Decimal = Decimal("0")
    id: UUID = field(default_factory=uuid4)
    validade: date | None = None
    atualizado_em: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.quantidade < 0:
            raise ValueError("Quantidade em estoque não pode ser negativa.")