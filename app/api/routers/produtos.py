from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_cadastrar_produto, get_usuario_atual
from app.api.schemas.produto import ProdutoCreate, ProdutoResponse
from app.application.use_cases.cadastrar_produto import CadastrarProduto, CadastrarProdutoInput
from app.domain.entities.usuario import Usuario

router = APIRouter(prefix="/produtos", tags=["Produtos"])


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