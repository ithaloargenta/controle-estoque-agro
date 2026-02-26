from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.produto import Produto


class ProdutoRepository(ABC):

    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        """Cria ou atualiza um produto."""
        ...

    @abstractmethod
    def buscar_por_id(self, produto_id: UUID) -> Produto | None:
        """Retorna um produto pelo ID ou None se não encontrar."""
        ...

    @abstractmethod
    def buscar_por_descricao(self, descricao: str) -> list[Produto]:
        """Retorna produtos que contenham o texto na descrição."""
        ...

    @abstractmethod
    def listar_ativos(self) -> list[Produto]:
        """Retorna todos os produtos ativos."""
        ...