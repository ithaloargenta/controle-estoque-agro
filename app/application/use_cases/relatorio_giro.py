from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemGiro:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    quantidade_saida: Decimal
    quantidade_saida_periodo_anterior: Decimal
    variacao_percentual: float | None


@dataclass
class RelatorioGiroInput:
    data_inicio: date
    data_fim: date


class RelatorioGiro:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioGiroInput) -> list[ItemGiro]:
        from sqlalchemy import func
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel

        tipos_saida = ('SAIDA', 'AJUSTE_SAIDA')

        # Calcula período anterior de mesmo tamanho
        duracao = (input.data_fim - input.data_inicio).days
        data_inicio_anterior = input.data_inicio - timedelta(days=duracao + 1)
        data_fim_anterior = input.data_inicio - timedelta(days=1)

        def buscar_saidas(data_inicio, data_fim):
            return (
                self.db.query(
                    MovimentacaoModel.produto_id,
                    func.sum(MovimentacaoModel.quantidade).label("total")
                )
                .filter(MovimentacaoModel.tipo.in_(tipos_saida))
                .filter(MovimentacaoModel.criado_em >= data_inicio)
                .filter(MovimentacaoModel.criado_em <= data_fim)
                .group_by(MovimentacaoModel.produto_id)
                .all()
            )

        saidas_atual = {r.produto_id: r.total for r in buscar_saidas(input.data_inicio, input.data_fim)}
        saidas_anterior = {r.produto_id: r.total for r in buscar_saidas(data_inicio_anterior, data_fim_anterior)}

        if not saidas_atual:
            return []

        produtos_ids = list(saidas_atual.keys())
        produtos = (
            self.db.query(ProdutoModel)
            .filter(ProdutoModel.id.in_(produtos_ids))
            .all()
        )
        produtos_map = {p.id: p for p in produtos}

        itens = []
        for produto_id, quantidade in saidas_atual.items():
            produto = produtos_map.get(produto_id)
            if not produto:
                continue

            qtd_anterior = saidas_anterior.get(produto_id, Decimal("0"))
            if qtd_anterior > 0:
                variacao = float((quantidade - qtd_anterior) / qtd_anterior * 100)
            else:
                variacao = None

            itens.append(ItemGiro(
                produto_id=produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                quantidade_saida=quantidade,
                quantidade_saida_periodo_anterior=qtd_anterior,
                variacao_percentual=variacao,
            ))

        return sorted(itens, key=lambda x: x.quantidade_saida, reverse=True)