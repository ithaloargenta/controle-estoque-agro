from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemVencimento:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    quantidade: Decimal
    validade: date
    dias_para_vencer: int


@dataclass
class RelatorioVencimentoInput:
    dias: int = 30


class RelatorioVencimento:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioVencimentoInput) -> list[ItemVencimento]:
        from app.infrastructure.models.estoque import EstoqueModel
        from app.infrastructure.models.produto import ProdutoModel

        hoje = date.today()
        limite = hoje + timedelta(days=input.dias)

        query = (
            self.db.query(EstoqueModel, ProdutoModel)
            .join(ProdutoModel, EstoqueModel.produto_id == ProdutoModel.id)
            .filter(ProdutoModel.ativo == True)
            .filter(EstoqueModel.validade != None)
            .filter(EstoqueModel.validade > hoje)
            .filter(EstoqueModel.validade <= limite)
            .filter(EstoqueModel.quantidade > 0)
        )

        resultados = query.all()

        itens = [
            ItemVencimento(
                produto_id=estoque.produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                localizacao=estoque.localizacao,
                quantidade=estoque.quantidade,
                validade=estoque.validade,
                dias_para_vencer=(estoque.validade - hoje).days,
            )
            for estoque, produto in resultados
        ]

        return sorted(itens, key=lambda x: x.dias_para_vencer)