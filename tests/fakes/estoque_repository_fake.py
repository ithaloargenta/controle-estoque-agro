from datetime import date
from uuid import UUID

from app.domain.entities.estoque import Estoque
from app.domain.repositories.estoque_repository import EstoqueRepository


class EstoqueRepositoryFake(EstoqueRepository):
    def __init__(self):
        self._dados: dict[UUID, Estoque] = {}

    def buscar_por_produto(self, produto_id: UUID) -> list[Estoque]:
        return [e for e in self._dados.values() if e.produto_id == produto_id]

    def buscar_por_produto_localizacao_validade(
        self,
        produto_id: UUID,
        localizacao: str,
        validade: date | None,
    ) -> Estoque | None:
        return next(
            (
                e for e in self._dados.values()
                if e.produto_id == produto_id
                and e.localizacao == localizacao
                and e.validade == validade
            ),
            None,
        )

    def listar_todos(self) -> list[Estoque]:
        return list(self._dados.values())