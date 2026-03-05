from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_cadastrar_produto, get_usuario_atual
from app.api.schemas.produto import ProdutoCreate, ProdutoResponse
from app.application.use_cases.cadastrar_produto import CadastrarProduto, CadastrarProdutoInput
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.produto_repository import ProdutoRepositoryImpl

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    repo = ProdutoRepositoryImpl(db)
    return repo.listar_ativos()


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_produto(
    body: ProdutoCreate,
    use_case: CadastrarProduto = Depends(get_cadastrar_produto),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        resultado = use_case.executar(
            CadastrarProdutoInput(
                descricao=body.descricao,
                unidade_comercial=body.unidade_comercial,
                ncm=body.ncm,
                requer_validade=body.requer_validade,
                estoque_minimo=body.estoque_minimo,
            )
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{produto_id}/desativar", status_code=status.HTTP_200_OK)
def desativar_produto(
    produto_id: str,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    repo = ProdutoRepositoryImpl(db)
    from uuid import UUID
    produto = repo.buscar_por_id(UUID(produto_id))
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")
    produto.ativo = False
    repo.salvar(produto)
    return {"ok": True, "mensagem": f"Produto '{produto.descricao}' desativado com sucesso."}