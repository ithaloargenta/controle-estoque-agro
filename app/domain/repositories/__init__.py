from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.fornecedor_repository import FornecedorRepository
from app.domain.repositories.estoque_repository import EstoqueRepository
from app.domain.repositories.movimentacao_repository import MovimentacaoRepository
from app.domain.repositories.usuario_repository import UsuarioRepository

__all__ = [
    "ProdutoRepository",
    "FornecedorRepository",
    "EstoqueRepository",
    "MovimentacaoRepository",
    "UsuarioRepository",
]