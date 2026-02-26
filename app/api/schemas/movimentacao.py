from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.movimentacao import TipoMovimentacao, Localizacao


class MovimentacaoCreate(BaseModel):
    produto_id: UUID
    localizacao: Localizacao
    tipo: TipoMovimentacao
    quantidade: Decimal = Field(gt=0)
    validade: date | None = None
    valor_unitario: Decimal | None = Field(default=None, gt=0)
    motivo: str | None = None


class MovimentacaoResponse(BaseModel):
    id: UUID
    produto_id: UUID
    localizacao: str
    tipo: str
    quantidade: Decimal
    validade: date | None
    valor_unitario: Decimal | None
    motivo: str | None

    model_config = {"from_attributes": True}