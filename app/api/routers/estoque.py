from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_consultar_estoque, get_consultar_estoque_enriquecido, get_usuario_atual
from app.api.schemas.estoque import EstoqueResponse, EstoqueEnriquecidoResponse
from app.application.use_cases.consultar_estoque import ConsultarEstoque, ConsultarEstoqueInput
from app.application.use_cases.consultar_estoque_enriquecido import ConsultarEstoqueEnriquecido, ConsultarEstoqueEnriquecidoInput
from app.domain.entities.usuario import Usuario

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("/", response_model=list[EstoqueResponse])
def consultar_estoque(
    produto_id: UUID | None = None,
    use_case: ConsultarEstoque = Depends(get_consultar_estoque),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    resultado = use_case.executar(ConsultarEstoqueInput(produto_id=produto_id))
    return resultado


@router.get("/enriquecido", response_model=list[EstoqueEnriquecidoResponse])
def consultar_estoque_enriquecido(
    produto_id: UUID | None = None,
    use_case: ConsultarEstoqueEnriquecido = Depends(get_consultar_estoque_enriquecido),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    resultado = use_case.executar(ConsultarEstoqueEnriquecidoInput(produto_id=produto_id))
    return resultado