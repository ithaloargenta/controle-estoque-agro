from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.models.usuario import UsuarioModel


class UsuarioRepositoryImpl(UsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, usuario: Usuario) -> Usuario:
        modelo = self.db.query(UsuarioModel).filter(
            UsuarioModel.id == usuario.id
        ).first()

        if modelo:
            modelo.nome = usuario.nome
            modelo.email = usuario.email
            modelo.senha_hash = usuario.senha_hash
            modelo.ativo = usuario.ativo
        else:
            modelo = UsuarioModel(
                id=usuario.id,
                nome=usuario.nome,
                email=usuario.email,
                senha_hash=usuario.senha_hash,
                ativo=usuario.ativo,
            )
            self.db.add(modelo)

        self.db.commit()
        self.db.refresh(modelo)
        return self._para_entidade(modelo)

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        modelo = self.db.query(UsuarioModel).filter(
            UsuarioModel.id == usuario_id
        ).first()
        return self._para_entidade(modelo) if modelo else None

    def buscar_por_email(self, email: str) -> Usuario | None:
        modelo = self.db.query(UsuarioModel).filter(
            UsuarioModel.email == email
        ).first()
        return self._para_entidade(modelo) if modelo else None

    def _para_entidade(self, modelo: UsuarioModel) -> Usuario:
        return Usuario(
            id=modelo.id,
            nome=modelo.nome,
            email=modelo.email,
            senha_hash=modelo.senha_hash,
            ativo=modelo.ativo,
            criado_em=modelo.criado_em,
        )