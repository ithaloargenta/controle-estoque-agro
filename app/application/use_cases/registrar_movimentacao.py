from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.domain.entities.movimentacao import Movimentacao, TipoMovimentacao, Localizacao
from app.domain.repositories.movimentacao_repository import MovimentacaoRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.estoque_repository import EstoqueRepository


@dataclass
class RegistrarMovimentacaoInput:
    produto_id: UUID
    localizacao: Localizacao
    tipo: TipoMovimentacao
    quantidade: Decimal
    usuario_id: UUID
    validade: date | None = None
    valor_unitario: Decimal | None = None
    motivo: str | None = None


@dataclass
class RegistrarMovimentacaoOutput:
    id: UUID
    produto_id: UUID
    localizacao: str
    tipo: str
    quantidade: Decimal
    validade: date | None
    valor_unitario: Decimal | None
    motivo: str | None


class RegistrarMovimentacao:
    def __init__(
        self,
        movimentacao_repository: MovimentacaoRepository,
        produto_repository: ProdutoRepository,
        estoque_repository: EstoqueRepository,
    ):
        self.movimentacao_repository = movimentacao_repository
        self.produto_repository = produto_repository
        self.estoque_repository = estoque_repository

    def executar(self, input: RegistrarMovimentacaoInput) -> RegistrarMovimentacaoOutput:
        # Verifica se o produto existe e está ativo
        produto = self.produto_repository.buscar_por_id(input.produto_id)
        if not produto:
            raise ValueError("Produto não encontrado.")
        if not produto.ativo:
            raise ValueError("Produto inativo não pode ter movimentações.")

        # Valida validade se o produto exigir
        produto.validar_validade_para_movimentacao(input.validade)

        # Para saídas, verifica se há saldo suficiente
        tipos_saida = {TipoMovimentacao.SAIDA, TipoMovimentacao.AJUSTE_SAIDA}
        if input.tipo in tipos_saida:
            estoque = self.estoque_repository.buscar_por_produto_localizacao_validade(
                produto_id=input.produto_id,
                localizacao=input.localizacao,
                validade=input.validade,
            )
            saldo_atual = estoque.quantidade if estoque else Decimal("0")
            if saldo_atual < input.quantidade:
                raise ValueError(
                    f"Saldo insuficiente. Disponível: {saldo_atual}, "
                    f"Solicitado: {input.quantidade}."
                )

        movimentacao = Movimentacao(
            produto_id=input.produto_id,
            localizacao=input.localizacao,
            tipo=input.tipo,
            quantidade=input.quantidade,
            usuario_id=input.usuario_id,
            validade=input.validade,
            valor_unitario=input.valor_unitario,
            motivo=input.motivo,
        )

        movimentacao_salva = self.movimentacao_repository.salvar(movimentacao)

        return RegistrarMovimentacaoOutput(
            id=movimentacao_salva.id,
            produto_id=movimentacao_salva.produto_id,
            localizacao=movimentacao_salva.localizacao,
            tipo=movimentacao_salva.tipo,
            quantidade=movimentacao_salva.quantidade,
            validade=movimentacao_salva.validade,
            valor_unitario=movimentacao_salva.valor_unitario,
            motivo=movimentacao_salva.motivo,
        )