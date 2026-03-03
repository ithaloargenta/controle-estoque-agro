from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository


@dataclass
class CadastrarProdutoInput:
    descricao: str
    unidade_comercial: str
    ncm: str | None = None
    requer_validade: bool = False
    estoque_minimo: int = 2


@dataclass
class CadastrarProdutoOutput:
    id: UUID
    descricao: str
    unidade_comercial: str
    ncm: str | None
    requer_validade: bool
    ativo: bool
    estoque_minimo: int


class CadastrarProduto:
    def __init__(self, produto_repository: ProdutoRepository):
        self.produto_repository = produto_repository

    def executar(self, input: CadastrarProdutoInput) -> CadastrarProdutoOutput:
        produto = Produto(
            descricao=input.descricao,
            unidade_comercial=input.unidade_comercial,
            ncm=input.ncm,
            requer_validade=input.requer_validade,
            estoque_minimo=input.estoque_minimo,
        )

        produto_salvo = self.produto_repository.salvar(produto)

        return CadastrarProdutoOutput(
            id=produto_salvo.id,
            descricao=produto_salvo.descricao,
            unidade_comercial=produto_salvo.unidade_comercial,
            ncm=produto_salvo.ncm,
            requer_validade=produto_salvo.requer_validade,
            ativo=produto_salvo.ativo,
            estoque_minimo=produto_salvo.estoque_minimo,
        )