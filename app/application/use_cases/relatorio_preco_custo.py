from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemPrecoCusto:
    movimentacao_id: UUID
    valor_unitario: Decimal
    quantidade: Decimal
    criado_em: datetime
    variacao_percentual: float | None


@dataclass
class RelatorioPrecoCustoInput:
    produto_id: UUID


@dataclass
class RelatorioPrecoCustoOutput:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    historico: list[ItemPrecoCusto]


class RelatorioPrecoCusto:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioPrecoCustoInput) -> RelatorioPrecoCustoOutput | None:
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel

        produto = (
            self.db.query(ProdutoModel)
            .filter(ProdutoModel.id == input.produto_id)
            .first()
        )

        if not produto:
            return None

        entradas = (
            self.db.query(MovimentacaoModel)
            .filter(MovimentacaoModel.produto_id == input.produto_id)
            .filter(MovimentacaoModel.tipo == 'ENTRADA')
            .filter(MovimentacaoModel.valor_unitario != None)
            .order_by(MovimentacaoModel.criado_em.asc())
            .all()
        )

        historico = []
        preco_anterior = None

        for entrada in entradas:
            if preco_anterior and preco_anterior > 0:
                variacao = float(
                    (entrada.valor_unitario - preco_anterior) / preco_anterior * 100
                )
            else:
                variacao = None

            historico.append(ItemPrecoCusto(
                movimentacao_id=entrada.id,
                valor_unitario=entrada.valor_unitario,
                quantidade=entrada.quantidade,
                criado_em=entrada.criado_em,
                variacao_percentual=round(variacao, 2) if variacao is not None else None,
            ))

            preco_anterior = entrada.valor_unitario

        return RelatorioPrecoCustoOutput(
            produto_id=produto.id,
            descricao=produto.descricao,
            ncm=produto.ncm,
            unidade_comercial=produto.unidade_comercial,
            historico=historico,
        )