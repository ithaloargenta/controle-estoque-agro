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


class EstoqueEnriquecidoResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    estoque_minimo: int
    abaixo_do_minimo: bool
    validade: date | None