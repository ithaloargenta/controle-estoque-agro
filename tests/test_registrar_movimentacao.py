import pytest
from decimal import Decimal
from uuid import uuid4

from app.application.use_cases.registrar_movimentacao import RegistrarMovimentacao, RegistrarMovimentacaoInput
from app.domain.entities.movimentacao import TipoMovimentacao, Localizacao
from app.domain.entities.produto import Produto
from tests.fakes.produto_repository_fake import ProdutoRepositoryFake
from tests.fakes.estoque_repository_fake import EstoqueRepositoryFake
from tests.fakes.movimentacao_repository_fake import MovimentacaoRepositoryFake


def make_use_case(produto_repo=None, estoque_repo=None, movimentacao_repo=None):
    return RegistrarMovimentacao(
        movimentacao_repository=movimentacao_repo or MovimentacaoRepositoryFake(),
        produto_repository=produto_repo or ProdutoRepositoryFake(),
        estoque_repository=estoque_repo or EstoqueRepositoryFake(),
    )


def make_produto(requer_validade=False, ativo=True) -> tuple[Produto, ProdutoRepositoryFake]:
    repo = ProdutoRepositoryFake()
    produto = Produto(
        descricao="Produto Teste",
        unidade_comercial="UN",
        requer_validade=requer_validade,
        ativo=ativo,
    )
    repo.salvar(produto)
    return produto, repo


def test_entrada_sucesso():
    produto, produto_repo = make_produto()
    use_case = make_use_case(produto_repo=produto_repo)

    resultado = use_case.executar(
        RegistrarMovimentacaoInput(
            produto_id=produto.id,
            localizacao=Localizacao.LOJA,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=Decimal("10"),
            usuario_id=uuid4(),
        )
    )

    assert resultado.tipo == TipoMovimentacao.ENTRADA
    assert resultado.quantidade == Decimal("10")


def test_produto_nao_encontrado():
    use_case = make_use_case()

    with pytest.raises(ValueError, match="Produto não encontrado."):
        use_case.executar(
            RegistrarMovimentacaoInput(
                produto_id=uuid4(),
                localizacao=Localizacao.LOJA,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=Decimal("10"),
                usuario_id=uuid4(),
            )
        )


def test_produto_inativo():
    produto, produto_repo = make_produto(ativo=False)
    use_case = make_use_case(produto_repo=produto_repo)

    with pytest.raises(ValueError, match="Produto inativo"):
        use_case.executar(
            RegistrarMovimentacaoInput(
                produto_id=produto.id,
                localizacao=Localizacao.LOJA,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=Decimal("10"),
                usuario_id=uuid4(),
            )
        )


def test_produto_requer_validade_sem_validade():
    produto, produto_repo = make_produto(requer_validade=True)
    use_case = make_use_case(produto_repo=produto_repo)

    with pytest.raises(ValueError, match="requer informação de validade"):
        use_case.executar(
            RegistrarMovimentacaoInput(
                produto_id=produto.id,
                localizacao=Localizacao.LOJA,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=Decimal("10"),
                usuario_id=uuid4(),
                validade=None,
            )
        )


def test_saida_saldo_insuficiente():
    produto, produto_repo = make_produto()
    use_case = make_use_case(produto_repo=produto_repo)

    with pytest.raises(ValueError, match="Saldo insuficiente"):
        use_case.executar(
            RegistrarMovimentacaoInput(
                produto_id=produto.id,
                localizacao=Localizacao.LOJA,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=Decimal("10"),
                usuario_id=uuid4(),
            )
        )


def test_ajuste_saida_sem_motivo():
    from app.domain.entities.estoque import Estoque

    produto, produto_repo = make_produto()
    estoque_repo = EstoqueRepositoryFake()

    estoque = Estoque(
        produto_id=produto.id,
        localizacao=Localizacao.LOJA,
        quantidade=Decimal("10"),
    )
    estoque_repo._dados[estoque.id] = estoque

    use_case = make_use_case(produto_repo=produto_repo, estoque_repo=estoque_repo)

    with pytest.raises(ValueError, match="Motivo é obrigatório"):
        use_case.executar(
            RegistrarMovimentacaoInput(
                produto_id=produto.id,
                localizacao=Localizacao.LOJA,
                tipo=TipoMovimentacao.AJUSTE_SAIDA,
                quantidade=Decimal("5"),
                usuario_id=uuid4(),
                motivo=None,
            )
        )