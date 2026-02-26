import pytest

from app.application.use_cases.cadastrar_usuario import CadastrarUsuario, CadastrarUsuarioInput
from tests.fakes.usuario_repository_fake import UsuarioRepositoryFake


def make_use_case():
    return CadastrarUsuario(UsuarioRepositoryFake())


def test_cadastrar_usuario_sucesso():
    use_case = make_use_case()
    resultado = use_case.executar(
        CadastrarUsuarioInput(
            nome="Ithalo",
            email="ithalo@estoque.com",
            senha="123456",
        )
    )
    assert resultado.nome == "Ithalo"
    assert resultado.email == "ithalo@estoque.com"
    assert resultado.ativo is True
    assert resultado.id is not None


def test_cadastrar_usuario_email_duplicado():
    use_case = make_use_case()
    use_case.executar(
        CadastrarUsuarioInput(
            nome="Ithalo",
            email="ithalo@estoque.com",
            senha="123456",
        )
    )
    with pytest.raises(ValueError, match="Já existe um usuário cadastrado com este email."):
        use_case.executar(
            CadastrarUsuarioInput(
                nome="Outro",
                email="ithalo@estoque.com",
                senha="654321",
            )
        )


def test_senha_nao_salva_em_texto_puro():
    repo = UsuarioRepositoryFake()
    use_case = CadastrarUsuario(repo)
    use_case.executar(
        CadastrarUsuarioInput(
            nome="Ithalo",
            email="ithalo@estoque.com",
            senha="123456",
        )
    )
    usuario_salvo = list(repo._dados.values())[0]
    assert usuario_salvo.senha_hash != "123456"
    assert len(usuario_salvo.senha_hash) > 20