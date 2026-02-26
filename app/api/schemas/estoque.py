from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class EstoqueResponse(BaseModel):
    id: UUID
    produto_id: UUID
    localizacao: str
    quantidade: Decimal
    validade: date | None

    model_config = {"from_attributes": True}