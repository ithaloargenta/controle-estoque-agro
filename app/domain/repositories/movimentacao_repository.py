from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.movimentacao import Movimentacao


class MovimentacaoRepository(ABC):

    @abstractmethod
    def salvar(self, movimentacao: Movimentacao) -> Movimentacao:
        """
        Registra uma movimentação.
        A trigger do banco atualiza o estoque automaticamente.
        """
        ...

    @abstractmethod
    def buscar_por_id(self, movimentacao_id: UUID) -> Movimentacao | None:
        """Retorna uma movimentação pelo ID ou None se não encontrar."""
        ...

    @abstractmethod
    def listar_por_produto(self, produto_id: UUID) -> list[Movimentacao]:
        """Retorna o histórico de movimentações de um produto."""
        ...