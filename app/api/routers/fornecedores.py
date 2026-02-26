from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_cadastrar_fornecedor, get_usuario_atual
from app.api.schemas.fornecedor import FornecedorCreate, FornecedorResponse
from app.application.use_cases.cadastrar_fornecedor import CadastrarFornecedor, CadastrarFornecedorInput
from app.domain.entities.usuario import Usuario

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


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