from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=6)


class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    ativo: bool

    model_config = {"from_attributes": True}