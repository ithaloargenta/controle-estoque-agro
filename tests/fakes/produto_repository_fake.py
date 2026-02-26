from uuid import UUID

from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository


class ProdutoRepositoryFake(ProdutoRepository):
    def __init__(self):
        self._dados: dict[UUID, Produto] = {}

    def salvar(self, produto: Produto) -> Produto:
        self._dados[produto.id] = produto
        return produto

    def buscar_por_id(self, produto_id: UUID) -> Produto | None:
        return self._dados.get(produto_id)

    def buscar_por_descricao(self, descricao: str) -> list[Produto]:
        return [
            p for p in self._dados.values()
            if descricao.lower() in p.descricao.lower()
        ]

    def listar_ativos(self) -> list[Produto]:
        return [p for p in self._dados.values() if p.ativo]