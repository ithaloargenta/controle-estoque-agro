from uuid import UUID

from app.domain.entities.movimentacao import Movimentacao
from app.domain.repositories.movimentacao_repository import MovimentacaoRepository


class MovimentacaoRepositoryFake(MovimentacaoRepository):
    def __init__(self):
        self._dados: dict[UUID, Movimentacao] = {}

    def salvar(self, movimentacao: Movimentacao) -> Movimentacao:
        self._dados[movimentacao.id] = movimentacao
        return movimentacao

    def buscar_por_id(self, movimentacao_id: UUID) -> Movimentacao | None:
        return self._dados.get(movimentacao_id)

    def listar_por_produto(self, produto_id: UUID) -> list[Movimentacao]:
        return [
            m for m in self._dados.values()
            if m.produto_id == produto_id
        ]