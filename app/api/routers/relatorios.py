from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import (
    get_relatorio_reposicao,
    get_relatorio_vencimento,
    get_relatorio_vencidos,
    get_relatorio_giro,
    get_relatorio_gasto_fornecedor,
    get_relatorio_historico,
    get_relatorio_sem_movimentacao,
    get_relatorio_valor_estoque,
    get_relatorio_curva_abc,
    get_relatorio_preco_custo,
    get_relatorio_sazonalidade,
    get_relatorio_comparativo_mensal,
    get_usuario_atual,
)
from app.application.use_cases.relatorio_reposicao import RelatorioReposicao, RelatorioReposicaoInput
from app.application.use_cases.relatorio_vencimento import RelatorioVencimento, RelatorioVencimentoInput
from app.application.use_cases.relatorio_vencidos import RelatorioVencidos
from app.application.use_cases.relatorio_giro import RelatorioGiro, RelatorioGiroInput
from app.application.use_cases.relatorio_gasto_fornecedor import RelatorioGastoFornecedor, RelatorioGastoFornecedorInput
from app.application.use_cases.relatorio_historico import RelatorioHistorico, RelatorioHistoricoInput
from app.application.use_cases.relatorio_sem_movimentacao import RelatorioSemMovimentacao, RelatorioSemMovimentacaoInput
from app.application.use_cases.relatorio_valor_estoque import RelatorioValorEstoque
from app.application.use_cases.relatorio_curva_abc import RelatorioCurvaABC, RelatorioCurvaABCInput
from app.application.use_cases.relatorio_preco_custo import RelatorioPrecoCusto, RelatorioPrecoCustoInput
from app.application.use_cases.relatorio_sazonalidade import RelatorioSazonalidade, RelatorioSazonalidadeInput
from app.application.use_cases.relatorio_comparativo_mensal import RelatorioComparativoMensal, RelatorioComparativoMensalInput
from app.domain.entities.usuario import Usuario

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


class ItemReposicaoResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade_atual: Decimal
    estoque_minimo: int
    quantidade_faltante: Decimal


class ItemVencimentoResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    validade: date
    dias_para_vencer: int


class ItemVencidoResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    validade: date
    dias_vencido: int


class ItemGiroResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    quantidade_saida: Decimal
    quantidade_saida_periodo_anterior: Decimal
    variacao_percentual: float | None


class ItemGastoFornecedorResponse(BaseModel):
    fornecedor_id: UUID | None
    razao_social: str
    total_entradas: int
    valor_total: Decimal


class ItemHistoricoResponse(BaseModel):
    movimentacao_id: UUID
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    tipo: str
    quantidade: Decimal
    valor_unitario: Decimal | None
    motivo: str | None
    usuario_id: UUID
    criado_em: datetime


class ItemSemMovimentacaoResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    quantidade_atual: Decimal
    ultima_movimentacao: datetime | None
    dias_parado: int


class ItemValorEstoqueResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    ultimo_preco_custo: Decimal | None
    valor_total: Decimal | None


class ValorEstoqueResponse(BaseModel):
    itens: list[ItemValorEstoqueResponse]
    valor_total_geral: Decimal


class ItemCurvaABCResponse(BaseModel):
    ncm_prefixo: str
    descricao_ncm: str
    quantidade_total_saida: Decimal
    percentual: float
    percentual_acumulado: float
    classificacao: str


class ItemPrecoCustoResponse(BaseModel):
    movimentacao_id: UUID
    valor_unitario: Decimal
    quantidade: Decimal
    criado_em: datetime
    variacao_percentual: float | None


class PrecoCustoResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    historico: list[ItemPrecoCustoResponse]


class ItemSazonalidadeResponse(BaseModel):
    ncm_prefixo: str
    descricao_ncm: str
    dados_mensais: dict[str, Decimal]


class MesComparativoResponse(BaseModel):
    entradas: Decimal
    saidas: Decimal
    valor_entradas: Decimal


class ItemComparativoMensalResponse(BaseModel):
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    mes_1: MesComparativoResponse
    mes_2: MesComparativoResponse
    variacao_entradas: float | None
    variacao_saidas: float | None


@router.get("/reposicao", response_model=list[ItemReposicaoResponse])
def relatorio_reposicao(
    use_case: RelatorioReposicao = Depends(get_relatorio_reposicao),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioReposicaoInput())


@router.get("/vencimento", response_model=list[ItemVencimentoResponse])
def relatorio_vencimento(
    dias: int = 30,
    use_case: RelatorioVencimento = Depends(get_relatorio_vencimento),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioVencimentoInput(dias=dias))


@router.get("/vencidos", response_model=list[ItemVencidoResponse])
def relatorio_vencidos(
    use_case: RelatorioVencidos = Depends(get_relatorio_vencidos),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar()


@router.get("/giro", response_model=list[ItemGiroResponse])
def relatorio_giro(
    data_inicio: date,
    data_fim: date,
    use_case: RelatorioGiro = Depends(get_relatorio_giro),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioGiroInput(
        data_inicio=data_inicio,
        data_fim=data_fim,
    ))


@router.get("/gasto-fornecedor", response_model=list[ItemGastoFornecedorResponse])
def relatorio_gasto_fornecedor(
    data_inicio: date,
    data_fim: date,
    use_case: RelatorioGastoFornecedor = Depends(get_relatorio_gasto_fornecedor),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioGastoFornecedorInput(
        data_inicio=data_inicio,
        data_fim=data_fim,
    ))


@router.get("/historico", response_model=list[ItemHistoricoResponse])
def relatorio_historico(
    data_inicio: date,
    data_fim: date,
    produto_id: UUID | None = None,
    tipo: str | None = None,
    use_case: RelatorioHistorico = Depends(get_relatorio_historico),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioHistoricoInput(
        data_inicio=data_inicio,
        data_fim=data_fim,
        produto_id=produto_id,
        tipo=tipo,
    ))


@router.get("/sem-movimentacao", response_model=list[ItemSemMovimentacaoResponse])
def relatorio_sem_movimentacao(
    dias: int = 90,
    use_case: RelatorioSemMovimentacao = Depends(get_relatorio_sem_movimentacao),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioSemMovimentacaoInput(dias=dias))


@router.get("/valor-estoque", response_model=ValorEstoqueResponse)
def relatorio_valor_estoque(
    use_case: RelatorioValorEstoque = Depends(get_relatorio_valor_estoque),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar()


@router.get("/curva-abc", response_model=list[ItemCurvaABCResponse])
def relatorio_curva_abc(
    data_inicio: date,
    data_fim: date,
    use_case: RelatorioCurvaABC = Depends(get_relatorio_curva_abc),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioCurvaABCInput(
        data_inicio=data_inicio,
        data_fim=data_fim,
    ))


@router.get("/preco-custo/{produto_id}", response_model=PrecoCustoResponse)
def relatorio_preco_custo(
    produto_id: UUID,
    use_case: RelatorioPrecoCusto = Depends(get_relatorio_preco_custo),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    resultado = use_case.executar(RelatorioPrecoCustoInput(produto_id=produto_id))
    if not resultado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return resultado


@router.get("/sazonalidade", response_model=list[ItemSazonalidadeResponse])
def relatorio_sazonalidade(
    ano: int,
    use_case: RelatorioSazonalidade = Depends(get_relatorio_sazonalidade),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioSazonalidadeInput(ano=ano))


@router.get("/comparativo-mensal", response_model=list[ItemComparativoMensalResponse])
def relatorio_comparativo_mensal(
    ano_mes_1: str,
    ano_mes_2: str,
    use_case: RelatorioComparativoMensal = Depends(get_relatorio_comparativo_mensal),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return use_case.executar(RelatorioComparativoMensalInput(
        ano_mes_1=ano_mes_1,
        ano_mes_2=ano_mes_2,
    ))