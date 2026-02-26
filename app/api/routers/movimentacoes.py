from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_registrar_movimentacao, get_usuario_atual
from app.api.schemas.movimentacao import MovimentacaoCreate, MovimentacaoResponse
from app.application.use_cases.registrar_movimentacao import RegistrarMovimentacao, RegistrarMovimentacaoInput
from app.domain.entities.usuario import Usuario

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])


@router.post("/", response_model=MovimentacaoResponse, status_code=status.HTTP_201_CREATED)
def registrar_movimentacao(
    body: MovimentacaoCreate,
    use_case: RegistrarMovimentacao = Depends(get_registrar_movimentacao),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        resultado = use_case.executar(
            RegistrarMovimentacaoInput(
                produto_id=body.produto_id,
                localizacao=body.localizacao,
                tipo=body.tipo,
                quantidade=body.quantidade,
                usuario_id=usuario_atual.id,
                validade=body.validade,
                valor_unitario=body.valor_unitario,
                motivo=body.motivo,
            )
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))