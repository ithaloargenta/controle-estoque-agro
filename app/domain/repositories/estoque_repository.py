from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.domain.entities.estoque import Estoque


class EstoqueRepository(ABC):

    @abstractmethod
    def buscar_por_produto(self, produto_id: UUID) -> list[Estoque]:
        """Retorna todos os registros de estoque de um produto."""
        ...

    @abstractmethod
    def buscar_por_produto_localizacao_validade(
        self,
        produto_id: UUID,
        localizacao: str,
        validade: date | None,
    ) -> Estoque | None:
        """
        Retorna o registro de estoque para a combinação exata de
        produto + localização + validade, ou None se não existir.
        """
        ...

    @abstractmethod
    def listar_todos(self) -> list[Estoque]:
        """Retorna todo o estoque atual."""
        ...