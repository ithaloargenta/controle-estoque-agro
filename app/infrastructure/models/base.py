from app.infrastructure.database.connection import Base  # noqa: F401

# Todos os modelos precisam ser importados aqui para que o SQLAlchemy
# registre os relacionamentos corretamente ao inicializar a aplicação.
from app.infrastructure.models.usuario import UsuarioModel  # noqa: F401
from app.infrastructure.models.fornecedor import FornecedorModel  # noqa: F401
from app.infrastructure.models.produto import ProdutoModel  # noqa: F401
from app.infrastructure.models.produto_fornecedor import ProdutoFornecedorModel  # noqa: F401
from app.infrastructure.models.estoque import EstoqueModel  # noqa: F401
from app.infrastructure.models.movimentacao import MovimentacaoModel  # noqa: F401