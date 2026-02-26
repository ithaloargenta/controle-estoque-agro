from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.usuario import Usuario


class UsuarioRepository(ABC):

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """Cria ou atualiza um usuário."""
        ...

    @abstractmethod
    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        """Retorna um usuário pelo ID ou None se não encontrar."""
        ...

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        """Retorna um usuário pelo email ou None se não encontrar."""
        ...