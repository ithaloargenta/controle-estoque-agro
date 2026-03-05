from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_usuario_atual
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.connection import get_db
from app.infrastructure.models.ncm_regra import NcmRegraModel

router = APIRouter(prefix="/ncm-regras", tags=["NCM Regras"])


class NcmRegraResponse(BaseModel):
    id: int
    ncm_prefixo: str
    descricao: str
    estoque_minimo: int

    class Config:
        from_attributes = True


class NcmRegraUpdate(BaseModel):
    estoque_minimo: int


@router.get("/", response_model=list[NcmRegraResponse])
def listar_regras(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return db.query(NcmRegraModel).order_by(NcmRegraModel.ncm_prefixo).all()


@router.patch("/{regra_id}", response_model=NcmRegraResponse)
def atualizar_regra(
    regra_id: int,
    body: NcmRegraUpdate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    regra = db.query(NcmRegraModel).filter(NcmRegraModel.id == regra_id).first()
    if not regra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regra não encontrada.")
    if body.estoque_minimo < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estoque mínimo não pode ser negativo.")
    regra.estoque_minimo = body.estoque_minimo
    db.commit()
    db.refresh(regra)
    return regra