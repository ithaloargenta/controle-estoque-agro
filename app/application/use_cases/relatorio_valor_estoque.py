from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemValorEstoque:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    ultimo_preco_custo: Decimal | None
    valor_total: Decimal | None


@dataclass
class RelatorioValorEstoqueOutput:
    itens: list[ItemValorEstoque]
    valor_total_geral: Decimal


class RelatorioValorEstoque:
    def __init__(self, db):
        self.db = db

    def executar(self) -> RelatorioValorEstoqueOutput:
        from sqlalchemy import func
        from app.infrastructure.models.estoque import EstoqueModel
        from app.infrastructure.models.produto import ProdutoModel
        from app.infrastructure.models.movimentacao import MovimentacaoModel

        # Busca estoque com produto
        estoques = (
            self.db.query(EstoqueModel, ProdutoModel)
            .join(ProdutoModel, EstoqueModel.produto_id == ProdutoModel.id)
            .filter(ProdutoModel.ativo == True)
            .filter(EstoqueModel.quantidade > 0)
            .all()
        )

        itens = []
        valor_total_geral = Decimal("0")

        for estoque, produto in estoques:
            # Busca último preço de custo nas entradas
            ultima_entrada = (
                self.db.query(MovimentacaoModel.valor_unitario)
                .filter(MovimentacaoModel.produto_id == produto.id)
                .filter(MovimentacaoModel.tipo == 'ENTRADA')
                .filter(MovimentacaoModel.valor_unitario != None)
                .order_by(MovimentacaoModel.criado_em.desc())
                .first()
            )

            ultimo_preco = ultima_entrada.valor_unitario if ultima_entrada else None
            valor_total = estoque.quantidade * ultimo_preco if ultimo_preco else None

            if valor_total:
                valor_total_geral += valor_total

            itens.append(ItemValorEstoque(
                produto_id=produto.id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                localizacao=estoque.localizacao,
                quantidade=estoque.quantidade,
                ultimo_preco_custo=ultimo_preco,
                valor_total=valor_total,
            ))

        itens_ordenados = sorted(
            itens,
            key=lambda x: x.valor_total or Decimal("0"),
            reverse=True
        )

        return RelatorioValorEstoqueOutput(
            itens=itens_ordenados,
            valor_total_geral=valor_total_geral,
        )