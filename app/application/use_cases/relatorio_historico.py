from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class ItemHistorico:
    movimentacao_id: UUID
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    localizacao: str
    tipo: str
    quantidade: Decimal
    valor_unitario: Decimal | None
    motivo: str | None
    usuario_id: UUID
    criado_em: datetime


@dataclass
class RelatorioHistoricoInput:
    data_inicio: date
    data_fim: date
    produto_id: UUID | None = None
    tipo: str | None = None


class RelatorioHistorico:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioHistoricoInput) -> list[ItemHistorico]:
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel

        query = (
            self.db.query(MovimentacaoModel, ProdutoModel)
            .join(ProdutoModel, MovimentacaoModel.produto_id == ProdutoModel.id)
            .filter(MovimentacaoModel.criado_em >= input.data_inicio)
            .filter(MovimentacaoModel.criado_em <= input.data_fim)
        )

        if input.produto_id:
            query = query.filter(MovimentacaoModel.produto_id == input.produto_id)

        if input.tipo:
            query = query.filter(MovimentacaoModel.tipo == input.tipo)

        resultados = query.order_by(MovimentacaoModel.criado_em.desc()).all()

        return [
            ItemHistorico(
                movimentacao_id=mov.id,
                produto_id=mov.produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                localizacao=mov.localizacao,
                tipo=mov.tipo,
                quantidade=mov.quantidade,
                valor_unitario=mov.valor_unitario,
                motivo=mov.motivo,
                usuario_id=mov.usuario_id,
                criado_em=mov.criado_em,
            )
            for mov, produto in resultados
        ]