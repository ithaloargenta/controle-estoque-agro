from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class ItemCurvaABC:
    ncm_prefixo: str
    descricao_ncm: str
    quantidade_total_saida: Decimal
    percentual: float
    percentual_acumulado: float
    classificacao: str


@dataclass
class RelatorioCurvaABCInput:
    data_inicio: date
    data_fim: date


class RelatorioCurvaABC:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioCurvaABCInput) -> list[ItemCurvaABC]:
        from sqlalchemy import func
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel
        from app.infrastructure.models.ncm_regra import NcmRegraModel

        tipos_saida = ('SAIDA', 'AJUSTE_SAIDA')

        resultados = (
            self.db.query(
                func.substr(ProdutoModel.ncm, 1, 4).label("ncm_prefixo"),
                func.sum(MovimentacaoModel.quantidade).label("total")
            )
            .join(ProdutoModel, MovimentacaoModel.produto_id == ProdutoModel.id)
            .filter(MovimentacaoModel.tipo.in_(tipos_saida))
            .filter(MovimentacaoModel.criado_em >= input.data_inicio)
            .filter(MovimentacaoModel.criado_em <= input.data_fim)
            .filter(ProdutoModel.ncm != None)
            .group_by(func.substr(ProdutoModel.ncm, 1, 4))
            .order_by(func.sum(MovimentacaoModel.quantidade).desc())
            .all()
        )

        if not resultados:
            return []

        total_geral = sum(r.total for r in resultados)

        # Busca descrições dos NCMs
        ncm_prefixos = [r.ncm_prefixo for r in resultados]
        regras = (
            self.db.query(NcmRegraModel)
            .filter(NcmRegraModel.ncm_prefixo.in_(ncm_prefixos))
            .all()
        )
        regras_map = {r.ncm_prefixo: r.descricao for r in regras}

        itens = []
        acumulado = 0.0

        for r in resultados:
            percentual = float(r.total / total_geral * 100)
            acumulado += percentual

            if acumulado <= 20:
                classificacao = "A"
            elif acumulado <= 50:
                classificacao = "B"
            else:
                classificacao = "C"

            itens.append(ItemCurvaABC(
                ncm_prefixo=r.ncm_prefixo,
                descricao_ncm=regras_map.get(r.ncm_prefixo, "NCM não mapeado"),
                quantidade_total_saida=r.total,
                percentual=round(percentual, 2),
                percentual_acumulado=round(acumulado, 2),
                classificacao=classificacao,
            ))

        return itens