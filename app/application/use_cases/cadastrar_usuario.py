from dataclasses import dataclass
from uuid import UUID

import bcrypt

from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import UsuarioRepository


@dataclass
class CadastrarUsuarioInput:
    nome: str
    email: str
    senha: str


@dataclass
class CadastrarUsuarioOutput:
    id: UUID
    nome: str
    email: str
    ativo: bool


class CadastrarUsuario:
    def __init__(self, usuario_repository: UsuarioRepository):
        self.usuario_repository = usuario_repository

    def executar(self, input: CadastrarUsuarioInput) -> CadastrarUsuarioOutput:
        # Verifica se o email já está cadastrado
        existente = self.usuario_repository.buscar_por_email(input.email)
        if existente:
            raise ValueError("Já existe um usuário cadastrado com este email.")

        # Hash da senha usando bcrypt diretamente
        senha_bytes = input.senha.encode("utf-8")
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")

        usuario = Usuario(
            nome=input.nome,
            email=input.email,
            senha_hash=senha_hash,
        )

        usuario_salvo = self.usuario_repository.salvar(usuario)

        return CadastrarUsuarioOutput(
            id=usuario_salvo.id,
            nome=usuario_salvo.nome,
            email=usuario_salvo.email,
            ativo=usuario_salvo.ativo,
        )