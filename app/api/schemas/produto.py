from uuid import UUID
from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    descricao: str = Field(min_length=2, max_length=200)
    unidade_comercial: str = Field(min_length=1, max_length=10)
    ncm: str | None = Field(default=None, min_length=8, max_length=8)
    requer_validade: bool = False
    estoque_minimo: int = Field(default=2, ge=0)


class ProdutoResponse(BaseModel):
    id: UUID
    descricao: str
    unidade_comercial: str
    ncm: str | None
    requer_validade: bool
    ativo: bool
    estoque_minimo: int

    model_config = {"from_attributes": True}