from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from app.domain.entities.movimentacao import Movimentacao, TipoMovimentacao, Localizacao
from app.domain.entities.produto import Produto
from app.domain.repositories.movimentacao_repository import MovimentacaoRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.fornecedor_repository import FornecedorRepository
from app.domain.entities.fornecedor import Fornecedor
from app.infrastructure.xml.nfe_parser import ItemNFe, Emitente


@dataclass
class ImportarXmlNFeInput:
    itens: list[ItemNFe]
    usuario_id: UUID
    localizacao: Localizacao = Localizacao.LOJA
    emitente: Emitente | None = None


@dataclass
class ImportarXmlNFeOutput:
    produtos_criados: int
    produtos_existentes: int
    movimentacoes_geradas: int
    fornecedor_criado: bool
    fornecedor_nome: str | None
    detalhes: list[str] = field(default_factory=list)


class ImportarXmlNFe:
    def __init__(
        self,
        produto_repository: ProdutoRepository,
        movimentacao_repository: MovimentacaoRepository,
        fornecedor_repository: FornecedorRepository,
    ):
        self.produto_repository = produto_repository
        self.movimentacao_repository = movimentacao_repository
        self.fornecedor_repository = fornecedor_repository

    def executar(self, input: ImportarXmlNFeInput) -> ImportarXmlNFeOutput:
        produtos_criados = 0
        produtos_existentes = 0
        movimentacoes_geradas = 0
        detalhes = []
        fornecedor_criado = False
        fornecedor_nome = None
        fornecedor = None

        # Busca ou cria fornecedor pelo CNPJ do emitente
        if input.emitente:
            fornecedor, fornecedor_criado = self._buscar_ou_criar_fornecedor(input.emitente)
            fornecedor_nome = fornecedor.razao_social
            if fornecedor_criado:
                detalhes.append(f"Fornecedor criado: '{fornecedor.razao_social}'")
            else:
                detalhes.append(f"Fornecedor já existente: '{fornecedor.razao_social}'")

        for item in input.itens:
            produto, criado = self._buscar_ou_criar_produto(item)

            if produto is None:
                detalhes.append(f"ERRO: Não foi possível processar '{item.descricao}'")
                continue

            if criado:
                produtos_criados += 1
                detalhes.append(f"Produto criado: '{item.descricao}'")
            else:
                produtos_existentes += 1
                detalhes.append(f"Produto já existente: '{item.descricao}'")

            # Gera movimentação de entrada
            movimentacao = Movimentacao(
                produto_id=produto.id,
                localizacao=input.localizacao,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=item.quantidade,
                usuario_id=input.usuario_id,
                valor_unitario=item.valor_unitario if item.valor_unitario > 0 else None,
                motivo="Importação de NF-e",
            )
            self.movimentacao_repository.salvar(movimentacao)
            movimentacoes_geradas += 1

        return ImportarXmlNFeOutput(
            produtos_criados=produtos_criados,
            produtos_existentes=produtos_existentes,
            movimentacoes_geradas=movimentacoes_geradas,
            fornecedor_criado=fornecedor_criado,
            fornecedor_nome=fornecedor_nome,
            detalhes=detalhes,
        )

    def _buscar_ou_criar_fornecedor(self, emitente: Emitente) -> tuple:
        existente = self.fornecedor_repository.buscar_por_cnpj(emitente.cnpj)
        if existente:
            return existente, False

        fornecedor = Fornecedor(
            razao_social=emitente.razao_social,
            cnpj=emitente.cnpj,
        )
        return self.fornecedor_repository.salvar(fornecedor), True

    def _buscar_ou_criar_produto(self, item: ItemNFe) -> tuple:
        existentes = self.produto_repository.buscar_por_descricao(item.descricao)
        if existentes:
            return existentes[0], False

        produto = Produto(
            descricao=item.descricao,
            unidade_comercial=item.unidade_comercial,
            ncm=item.ncm if item.ncm else None,
            requer_validade=False,
        )
        return self.produto_repository.salvar(produto), True