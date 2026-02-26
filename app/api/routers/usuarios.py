from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_cadastrar_usuario
from app.api.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.application.use_cases.cadastrar_usuario import CadastrarUsuario, CadastrarUsuarioInput

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(
    body: UsuarioCreate,
    use_case: CadastrarUsuario = Depends(get_cadastrar_usuario),
):
    try:
        resultado = use_case.executar(
            CadastrarUsuarioInput(
                nome=body.nome,
                email=body.email,
                senha=body.senha,
            )
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))