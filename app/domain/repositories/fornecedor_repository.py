from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.fornecedor import Fornecedor


class FornecedorRepository(ABC):

    @abstractmethod
    def salvar(self, fornecedor: Fornecedor) -> Fornecedor:
        """Cria ou atualiza um fornecedor."""
        ...

    @abstractmethod
    def buscar_por_id(self, fornecedor_id: UUID) -> Fornecedor | None:
        """Retorna um fornecedor pelo ID ou None se não encontrar."""
        ...

    @abstractmethod
    def buscar_por_cnpj(self, cnpj: str) -> Fornecedor | None:
        """Retorna um fornecedor pelo CNPJ ou None se não encontrar."""
        ...

    @abstractmethod
    def listar_ativos(self) -> list[Fornecedor]:
        """Retorna todos os fornecedores ativos."""
        ...