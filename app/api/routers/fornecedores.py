from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_cadastrar_fornecedor, get_usuario_atual
from app.api.schemas.fornecedor import FornecedorCreate, FornecedorResponse
from app.application.use_cases.cadastrar_fornecedor import CadastrarFornecedor, CadastrarFornecedorInput
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.fornecedor_repository import FornecedorRepositoryImpl

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


@router.get("/", response_model=list[FornecedorResponse])
def listar_fornecedores(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    repo = FornecedorRepositoryImpl(db)
    return repo.listar_ativos()


@router.post("/", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_fornecedor(
    body: FornecedorCreate,
    use_case: CadastrarFornecedor = Depends(get_cadastrar_fornecedor),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        resultado = use_case.executar(
            CadastrarFornecedorInput(
                razao_social=body.razao_social,
                cnpj=body.cnpj,
            )
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{fornecedor_id}/produtos", status_code=status.HTTP_200_OK)
def vincular_produto(
    fornecedor_id: str,
    body: dict,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    from app.infrastructure.models.produto_fornecedor import ProdutoFornecedorModel
    from uuid import UUID

    existente = db.query(ProdutoFornecedorModel).filter(
        ProdutoFornecedorModel.produto_id == UUID(body["produto_id"]),
        ProdutoFornecedorModel.fornecedor_id == UUID(fornecedor_id),
    ).first()

    if existente:
        return {"ok": True, "mensagem": "Vínculo já existe."}

    vinculo = ProdutoFornecedorModel(
        produto_id=UUID(body["produto_id"]),
        fornecedor_id=UUID(fornecedor_id),
        codigo_fornecedor=body.get("codigo_fornecedor"),
    )
    db.add(vinculo)
    db.commit()
    return {"ok": True, "mensagem": "Produto vinculado com sucesso."}