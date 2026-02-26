from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.auth import verificar_token
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.usuario_repository import UsuarioRepositoryImpl
from app.infrastructure.repositories.produto_repository import ProdutoRepositoryImpl
from app.infrastructure.repositories.fornecedor_repository import FornecedorRepositoryImpl
from app.infrastructure.repositories.estoque_repository import EstoqueRepositoryImpl
from app.infrastructure.repositories.movimentacao_repository import MovimentacaoRepositoryImpl
from app.application.use_cases.cadastrar_produto import CadastrarProduto
from app.application.use_cases.cadastrar_fornecedor import CadastrarFornecedor
from app.application.use_cases.registrar_movimentacao import RegistrarMovimentacao
from app.application.use_cases.consultar_estoque import ConsultarEstoque
from app.application.use_cases.cadastrar_usuario import CadastrarUsuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = verificar_token(token)
        usuario_id: str = payload.get("sub")
        if not usuario_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UsuarioRepositoryImpl(db)
    usuario = repo.buscar_por_id(usuario_id)
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return usuario


def get_cadastrar_produto(db: Session = Depends(get_db)) -> CadastrarProduto:
    return CadastrarProduto(ProdutoRepositoryImpl(db))


def get_cadastrar_fornecedor(db: Session = Depends(get_db)) -> CadastrarFornecedor:
    return CadastrarFornecedor(FornecedorRepositoryImpl(db))


def get_registrar_movimentacao(db: Session = Depends(get_db)) -> RegistrarMovimentacao:
    return RegistrarMovimentacao(
        MovimentacaoRepositoryImpl(db),
        ProdutoRepositoryImpl(db),
        EstoqueRepositoryImpl(db),
    )


def get_consultar_estoque(db: Session = Depends(get_db)) -> ConsultarEstoque:
    return ConsultarEstoque(EstoqueRepositoryImpl(db))


def get_cadastrar_usuario(db: Session = Depends(get_db)) -> CadastrarUsuario:
    return CadastrarUsuario(UsuarioRepositoryImpl(db))

from app.application.use_cases.importar_xml_nfe import ImportarXmlNFe

def get_importar_xml_nfe(db: Session = Depends(get_db)) -> ImportarXmlNFe:
    return ImportarXmlNFe(
        ProdutoRepositoryImpl(db),
        MovimentacaoRepositoryImpl(db),
    )