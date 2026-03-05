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
        FornecedorRepositoryImpl(db),
        db=db,
    )

from app.application.use_cases.consultar_estoque_enriquecido import ConsultarEstoqueEnriquecido

def get_consultar_estoque_enriquecido(db: Session = Depends(get_db)) -> ConsultarEstoqueEnriquecido:
    return ConsultarEstoqueEnriquecido(db)

from app.application.use_cases.relatorio_reposicao import RelatorioReposicao

def get_relatorio_reposicao(db: Session = Depends(get_db)) -> RelatorioReposicao:
    return RelatorioReposicao(db)

from app.application.use_cases.relatorio_vencimento import RelatorioVencimento

def get_relatorio_vencimento(db: Session = Depends(get_db)) -> RelatorioVencimento:
    return RelatorioVencimento(db)

from app.application.use_cases.relatorio_vencidos import RelatorioVencidos

def get_relatorio_vencidos(db: Session = Depends(get_db)) -> RelatorioVencidos:
    return RelatorioVencidos(db)

from app.application.use_cases.relatorio_giro import RelatorioGiro

def get_relatorio_giro(db: Session = Depends(get_db)) -> RelatorioGiro:
    return RelatorioGiro(db)

from app.application.use_cases.relatorio_gasto_fornecedor import RelatorioGastoFornecedor

def get_relatorio_gasto_fornecedor(db: Session = Depends(get_db)) -> RelatorioGastoFornecedor:
    return RelatorioGastoFornecedor(db)

from app.application.use_cases.relatorio_historico import RelatorioHistorico

def get_relatorio_historico(db: Session = Depends(get_db)) -> RelatorioHistorico:
    return RelatorioHistorico(db)

from app.application.use_cases.relatorio_sem_movimentacao import RelatorioSemMovimentacao

def get_relatorio_sem_movimentacao(db: Session = Depends(get_db)) -> RelatorioSemMovimentacao:
    return RelatorioSemMovimentacao(db)

from app.application.use_cases.relatorio_valor_estoque import RelatorioValorEstoque

def get_relatorio_valor_estoque(db: Session = Depends(get_db)) -> RelatorioValorEstoque:
    return RelatorioValorEstoque(db)

from app.application.use_cases.relatorio_curva_abc import RelatorioCurvaABC

def get_relatorio_curva_abc(db: Session = Depends(get_db)) -> RelatorioCurvaABC:
    return RelatorioCurvaABC(db)

from app.application.use_cases.relatorio_preco_custo import RelatorioPrecoCusto

def get_relatorio_preco_custo(db: Session = Depends(get_db)) -> RelatorioPrecoCusto:
    return RelatorioPrecoCusto(db)

from app.application.use_cases.relatorio_sazonalidade import RelatorioSazonalidade

def get_relatorio_sazonalidade(db: Session = Depends(get_db)) -> RelatorioSazonalidade:
    return RelatorioSazonalidade(db)
from app.application.use_cases.relatorio_comparativo_mensal import RelatorioComparativoMensal

def get_relatorio_comparativo_mensal(db: Session = Depends(get_db)) -> RelatorioComparativoMensal:
    return RelatorioComparativoMensal(db)