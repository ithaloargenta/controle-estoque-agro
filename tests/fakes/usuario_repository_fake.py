from uuid import UUID

from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import UsuarioRepository


class UsuarioRepositoryFake(UsuarioRepository):
    def __init__(self):
        self._dados: dict[UUID, Usuario] = {}

    def salvar(self, usuario: Usuario) -> Usuario:
        self._dados[usuario.id] = usuario
        return usuario

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self._dados.get(usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        return next(
            (u for u in self._dados.values() if u.email == email),
            None,
        )