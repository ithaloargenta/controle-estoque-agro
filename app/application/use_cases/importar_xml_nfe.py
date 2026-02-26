from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from app.domain.entities.movimentacao import Movimentacao, TipoMovimentacao, Localizacao
from app.domain.entities.produto import Produto
from app.domain.repositories.movimentacao_repository import MovimentacaoRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.infrastructure.xml.nfe_parser import ItemNFe


@dataclass
class ImportarXmlNFeInput:
    itens: list[ItemNFe]
    usuario_id: UUID
    localizacao: Localizacao = Localizacao.LOJA


@dataclass
class ImportarXmlNFeOutput:
    produtos_criados: int
    produtos_existentes: int
    movimentacoes_geradas: int
    detalhes: list[str] = field(default_factory=list)


class ImportarXmlNFe:
    def __init__(
        self,
        produto_repository: ProdutoRepository,
        movimentacao_repository: MovimentacaoRepository,
    ):
        self.produto_repository = produto_repository
        self.movimentacao_repository = movimentacao_repository

    def executar(self, input: ImportarXmlNFeInput) -> ImportarXmlNFeOutput:
        produtos_criados = 0
        produtos_existentes = 0
        movimentacoes_geradas = 0
        detalhes = []

        for item in input.itens:
            # Busca produto pelo NCM e descrição
            produto = self._buscar_ou_criar_produto(item)

            if produto is None:
                detalhes.append(f"ERRO: Não foi possível processar '{item.descricao}'")
                continue

            # Verifica se o produto foi criado ou já existia
            produtos_existentes_antes = self.produto_repository.buscar_por_descricao(
                item.descricao
            )
            if len(produtos_existentes_antes) > 1:
                produtos_existentes += 1
                detalhes.append(f"Produto já existente: '{item.descricao}'")
            else:
                produtos_criados += 1
                detalhes.append(f"Produto criado: '{item.descricao}'")

            # Gera movimentação de entrada
            movimentacao = Movimentacao(
                produto_id=produto.id,
                localizacao=input.localizacao,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=item.quantidade,
                usuario_id=input.usuario_id,
                valor_unitario=item.valor_unitario if item.valor_unitario > 0 else None,
                motivo=f"Importação de NF-e",
            )
            self.movimentacao_repository.salvar(movimentacao)
            movimentacoes_geradas += 1

        return ImportarXmlNFeOutput(
            produtos_criados=produtos_criados,
            produtos_existentes=produtos_existentes,
            movimentacoes_geradas=movimentacoes_geradas,
            detalhes=detalhes,
        )

    def _buscar_ou_criar_produto(self, item: ItemNFe) -> Produto | None:
        # Busca por descrição exata primeiro
        existentes = self.produto_repository.buscar_por_descricao(item.descricao)
        if existentes:
            return existentes[0]

        # Cria novo produto
        produto = Produto(
            descricao=item.descricao,
            unidade_comercial=item.unidade_comercial,
            ncm=item.ncm if item.ncm else None,
            requer_validade=False,
        )
        return self.produto_repository.salvar(produto)