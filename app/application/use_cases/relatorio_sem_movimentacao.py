from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemSemMovimentacao:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    quantidade_atual: Decimal
    ultima_movimentacao: datetime | None
    dias_parado: int


@dataclass
class RelatorioSemMovimentacaoInput:
    dias: int = 90


class RelatorioSemMovimentacao:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioSemMovimentacaoInput) -> list[ItemSemMovimentacao]:
        from sqlalchemy import func
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel
        from app.infrastructure.models.estoque import EstoqueModel

        limite = datetime.now() - timedelta(days=input.dias)

        # Busca última movimentação por produto
        ultima_mov = (
            self.db.query(
                MovimentacaoModel.produto_id,
                func.max(MovimentacaoModel.criado_em).label("ultima")
            )
            .group_by(MovimentacaoModel.produto_id)
            .subquery()
        )

        # Busca produtos ativos sem movimentação no período
        query = (
            self.db.query(ProdutoModel, ultima_mov.c.ultima)
            .outerjoin(ultima_mov, ProdutoModel.id == ultima_mov.c.produto_id)
            .filter(ProdutoModel.ativo == True)
            .filter(
                (ultima_mov.c.ultima == None) |
                (ultima_mov.c.ultima < limite)
            )
        )

        resultados = query.all()

        itens = []
        for produto, ultima in resultados:
            # Busca quantidade atual em estoque
            estoque = (
                self.db.query(func.sum(EstoqueModel.quantidade))
                .filter(EstoqueModel.produto_id == produto.id)
                .scalar() or Decimal("0")
            )

            if ultima:
                dias_parado = (datetime.now() - ultima).days
            else:
                dias_parado = input.dias

            itens.append(ItemSemMovimentacao(
                produto_id=produto.id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                quantidade_atual=estoque,
                ultima_movimentacao=ultima,
                dias_parado=dias_parado,
            ))

        return sorted(itens, key=lambda x: x.dias_parado, reverse=True)