from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemReposicao:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade_atual: Decimal
    estoque_minimo: int
    quantidade_faltante: Decimal


@dataclass
class RelatorioReposicaoInput:
    apenas_criticos: bool = False


class RelatorioReposicao:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioReposicaoInput) -> list[ItemReposicao]:
        from app.infrastructure.models.estoque import EstoqueModel
        from app.infrastructure.models.produto import ProdutoModel

        query = (
            self.db.query(EstoqueModel, ProdutoModel)
            .join(ProdutoModel, EstoqueModel.produto_id == ProdutoModel.id)
            .filter(ProdutoModel.ativo == True)
            .filter(EstoqueModel.quantidade <= ProdutoModel.estoque_minimo)
        )

        resultados = query.all()

        itens = [
            ItemReposicao(
                produto_id=estoque.produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                localizacao=estoque.localizacao,
                quantidade_atual=estoque.quantidade,
                estoque_minimo=produto.estoque_minimo,
                quantidade_faltante=Decimal(produto.estoque_minimo) - estoque.quantidade,
            )
            for estoque, produto in resultados
        ]

        return sorted(itens, key=lambda x: x.quantidade_faltante, reverse=True)