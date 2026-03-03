from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class EstoqueEnriquecidoItem:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    estoque_minimo: int
    abaixo_do_minimo: bool
    validade: date | None


@dataclass
class ConsultarEstoqueEnriquecidoInput:
    produto_id: UUID | None = None


class ConsultarEstoqueEnriquecido:
    def __init__(self, db):
        self.db = db

    def executar(self, input: ConsultarEstoqueEnriquecidoInput) -> list[EstoqueEnriquecidoItem]:
        from app.infrastructure.models.estoque import EstoqueModel
        from app.infrastructure.models.produto import ProdutoModel

        query = (
            self.db.query(EstoqueModel, ProdutoModel)
            .join(ProdutoModel, EstoqueModel.produto_id == ProdutoModel.id)
            .filter(ProdutoModel.ativo == True)
        )

        if input.produto_id:
            query = query.filter(EstoqueModel.produto_id == input.produto_id)

        resultados = query.all()

        return [
            EstoqueEnriquecidoItem(
                produto_id=estoque.produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                localizacao=estoque.localizacao,
                quantidade=estoque.quantidade,
                estoque_minimo=produto.estoque_minimo,
                abaixo_do_minimo=estoque.quantidade <= produto.estoque_minimo,
                validade=estoque.validade,
            )
            for estoque, produto in resultados
        ]