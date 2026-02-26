from uuid import UUID
from pydantic import BaseModel, Field


class FornecedorCreate(BaseModel):
    razao_social: str = Field(min_length=2, max_length=150)
    cnpj: str | None = Field(default=None, min_length=14, max_length=14)


class FornecedorResponse(BaseModel):
    id: UUID
    razao_social: str
    cnpj: str | None
    ativo: bool

    model_config = {"from_attributes": True}