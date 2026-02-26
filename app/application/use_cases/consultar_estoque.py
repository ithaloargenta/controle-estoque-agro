from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.domain.repositories.estoque_repository import EstoqueRepository


@dataclass
class EstoqueItemOutput:
    id: UUID
    produto_id: UUID
    localizacao: str
    quantidade: Decimal
    validade: date | None


@dataclass
class ConsultarEstoqueInput:
    produto_id: UUID | None = None


class ConsultarEstoque:
    def __init__(self, estoque_repository: EstoqueRepository):
        self.estoque_repository = estoque_repository

    def executar(self, input: ConsultarEstoqueInput) -> list[EstoqueItemOutput]:
        if input.produto_id:
            registros = self.estoque_repository.buscar_por_produto(input.produto_id)
        else:
            registros = self.estoque_repository.listar_todos()

        return [
            EstoqueItemOutput(
                id=registro.id,
                produto_id=registro.produto_id,
                localizacao=registro.localizacao,
                quantidade=registro.quantidade,
                validade=registro.validade,
            )
            for registro in registros
        ]