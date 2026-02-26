import pytest

from app.application.use_cases.cadastrar_produto import CadastrarProduto, CadastrarProdutoInput
from tests.fakes.produto_repository_fake import ProdutoRepositoryFake


def make_use_case():
    return CadastrarProduto(ProdutoRepositoryFake())


def test_cadastrar_produto_sucesso():
    use_case = make_use_case()
    resultado = use_case.executar(
        CadastrarProdutoInput(
            descricao="Ivermectina 1%",
            unidade_comercial="UN",
            ncm="30021590",
            requer_validade=True,
        )
    )
    assert resultado.descricao == "Ivermectina 1%"
    assert resultado.unidade_comercial == "UN"
    assert resultado.ncm == "30021590"
    assert resultado.requer_validade is True
    assert resultado.ativo is True
    assert resultado.id is not None


def test_cadastrar_produto_sem_ncm():
    use_case = make_use_case()
    resultado = use_case.executar(
        CadastrarProdutoInput(
            descricao="Ração para Gado",
            unidade_comercial="SC",
        )
    )
    assert resultado.ncm is None
    assert resultado.requer_validade is False


def test_cadastrar_dois_produtos_ids_diferentes():
    use_case = make_use_case()
    r1 = use_case.executar(CadastrarProdutoInput(descricao="Produto A", unidade_comercial="UN"))
    r2 = use_case.executar(CadastrarProdutoInput(descricao="Produto B", unidade_comercial="UN"))
    assert r1.id != r2.id