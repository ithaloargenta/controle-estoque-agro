from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemVencido:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    validade: date
    dias_vencido: int


class RelatorioVencidos:
    def __init__(self, db):
        self.db = db

    def executar(self) -> list[ItemVencido]:
        from app.infrastructure.models.estoque import EstoqueModel
        from app.infrastructure.models.produto import ProdutoModel

        hoje = date.today()

        query = (
            self.db.query(EstoqueModel, ProdutoModel)
            .join(ProdutoModel, EstoqueModel.produto_id == ProdutoModel.id)
            .filter(ProdutoModel.ativo == True)
            .filter(EstoqueModel.validade != None)
            .filter(EstoqueModel.validade < hoje)
            .filter(EstoqueModel.quantidade > 0)
        )

        resultados = query.all()

        itens = [
            ItemVencido(
                produto_id=estoque.produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                localizacao=estoque.localizacao,
                quantidade=estoque.quantidade,
                validade=estoque.validade,
                dias_vencido=(hoje - estoque.validade).days,
            )
            for estoque, produto in resultados
        ]

        return sorted(itens, key=lambda x: x.dias_vencido, reverse=True)