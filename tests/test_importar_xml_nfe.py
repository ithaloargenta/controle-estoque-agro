import pytest
from decimal import Decimal
from uuid import uuid4

from app.application.use_cases.importar_xml_nfe import ImportarXmlNFe, ImportarXmlNFeInput
from app.domain.entities.movimentacao import Localizacao
from app.infrastructure.xml.nfe_parser import ItemNFe, Emitente
from tests.fakes.produto_repository_fake import ProdutoRepositoryFake
from tests.fakes.movimentacao_repository_fake import MovimentacaoRepositoryFake
from tests.fakes.fornecedor_repository_fake import FornecedorRepositoryFake


def make_itens() -> list[ItemNFe]:
    return [
        ItemNFe(
            descricao="Produto Teste NF-e",
            ncm="30021590",
            unidade_comercial="UN",
            quantidade=Decimal("10"),
            valor_unitario=Decimal("50.00"),
            codigo_fornecedor="SKU-001",
        )
    ]


def make_emitente() -> Emitente:
    return Emitente(cnpj="12345678000195", razao_social="Fornecedor Teste LTDA")


def make_use_case(produto_repo=None, mov_repo=None, forn_repo=None):
    return ImportarXmlNFe(
        produto_repository=produto_repo or ProdutoRepositoryFake(),
        movimentacao_repository=mov_repo or MovimentacaoRepositoryFake(),
        fornecedor_repository=forn_repo or FornecedorRepositoryFake(),
        db=None,
    )


def test_importar_cria_produto_novo():
    produto_repo = ProdutoRepositoryFake()
    use_case = make_use_case(produto_repo=produto_repo)

    resultado = use_case.executar(ImportarXmlNFeInput(
        itens=make_itens(),
        usuario_id=uuid4(),
        localizacao=Localizacao.LOJA,
    ))

    assert resultado.produtos_criados == 1
    assert resultado.produtos_existentes == 0
    assert resultado.movimentacoes_geradas == 1


def test_importar_produto_ja_existente():
    from app.domain.entities.produto import Produto

    produto_repo = ProdutoRepositoryFake()
    produto = Produto(descricao="Produto Teste NF-e", unidade_comercial="UN")
    produto_repo.salvar(produto)

    use_case = make_use_case(produto_repo=produto_repo)

    resultado = use_case.executar(ImportarXmlNFeInput(
        itens=make_itens(),
        usuario_id=uuid4(),
        localizacao=Localizacao.LOJA,
    ))

    assert resultado.produtos_criados == 0
    assert resultado.produtos_existentes == 1
    assert resultado.movimentacoes_geradas == 1


def test_importar_cria_fornecedor_novo():
    forn_repo = FornecedorRepositoryFake()
    use_case = make_use_case(forn_repo=forn_repo)

    resultado = use_case.executar(ImportarXmlNFeInput(
        itens=make_itens(),
        usuario_id=uuid4(),
        localizacao=Localizacao.LOJA,
        emitente=make_emitente(),
    ))

    assert resultado.fornecedor_criado is True
    assert resultado.fornecedor_nome == "Fornecedor Teste LTDA"
    assert len(forn_repo.listar_ativos()) == 1


def test_importar_fornecedor_ja_existente():
    from app.domain.entities.fornecedor import Fornecedor

    forn_repo = FornecedorRepositoryFake()
    fornecedor = Fornecedor(razao_social="Fornecedor Teste LTDA", cnpj="12345678000195")
    forn_repo.salvar(fornecedor)

    use_case = make_use_case(forn_repo=forn_repo)

    resultado = use_case.executar(ImportarXmlNFeInput(
        itens=make_itens(),
        usuario_id=uuid4(),
        localizacao=Localizacao.LOJA,
        emitente=make_emitente(),
    ))

    assert resultado.fornecedor_criado is False
    assert len(forn_repo.listar_ativos()) == 1


def test_importar_sem_emitente():
    use_case = make_use_case()

    resultado = use_case.executar(ImportarXmlNFeInput(
        itens=make_itens(),
        usuario_id=uuid4(),
        localizacao=Localizacao.LOJA,
        emitente=None,
    ))

    assert resultado.fornecedor_nome is None
    assert resultado.movimentacoes_geradas == 1