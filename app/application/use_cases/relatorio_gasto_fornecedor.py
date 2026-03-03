from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemGastoFornecedor:
    fornecedor_id: UUID | None
    razao_social: str
    total_entradas: int
    valor_total: Decimal


@dataclass
class RelatorioGastoFornecedorInput:
    data_inicio: date
    data_fim: date


class RelatorioGastoFornecedor:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioGastoFornecedorInput) -> list[ItemGastoFornecedor]:
        from sqlalchemy import func
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel
        from app.infrastructure.models.produto_fornecedor import ProdutoFornecedorModel
        from app.infrastructure.models.fornecedor import FornecedorModel

        # Busca entradas no período com valor unitário preenchido
        entradas = (
            self.db.query(MovimentacaoModel)
            .filter(MovimentacaoModel.tipo == 'ENTRADA')
            .filter(MovimentacaoModel.valor_unitario != None)
            .filter(MovimentacaoModel.criado_em >= input.data_inicio)
            .filter(MovimentacaoModel.criado_em <= input.data_fim)
            .all()
        )

        if not entradas:
            return []

        # Agrupa por fornecedor via produto_fornecedor
        gastos: dict[str, dict] = {}

        for entrada in entradas:
            # Busca fornecedor vinculado ao produto
            vinculo = (
                self.db.query(ProdutoFornecedorModel, FornecedorModel)
                .join(FornecedorModel, ProdutoFornecedorModel.fornecedor_id == FornecedorModel.id)
                .filter(ProdutoFornecedorModel.produto_id == entrada.produto_id)
                .first()
            )

            if vinculo:
                _, fornecedor = vinculo
                chave = str(fornecedor.id)
                nome = fornecedor.razao_social
                fornecedor_id = fornecedor.id
            else:
                chave = "sem_fornecedor"
                nome = "Fornecedor não vinculado"
                fornecedor_id = None

            valor = entrada.valor_unitario * entrada.quantidade

            if chave not in gastos:
                gastos[chave] = {
                    "fornecedor_id": fornecedor_id,
                    "razao_social": nome,
                    "total_entradas": 0,
                    "valor_total": Decimal("0"),
                }

            gastos[chave]["total_entradas"] += 1
            gastos[chave]["valor_total"] += valor

        itens = [
            ItemGastoFornecedor(
                fornecedor_id=g["fornecedor_id"],
                razao_social=g["razao_social"],
                total_entradas=g["total_entradas"],
                valor_total=g["valor_total"],
            )
            for g in gastos.values()
        ]

        return sorted(itens, key=lambda x: x.valor_total, reverse=True)