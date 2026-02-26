from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.movimentacao import Movimentacao, TipoMovimentacao, Localizacao
from app.domain.repositories.movimentacao_repository import MovimentacaoRepository
from app.infrastructure.models.movimentacao import MovimentacaoModel


class MovimentacaoRepositoryImpl(MovimentacaoRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, movimentacao: Movimentacao) -> Movimentacao:
        modelo = MovimentacaoModel(
            id=movimentacao.id,
            produto_id=movimentacao.produto_id,
            localizacao=movimentacao.localizacao.value,
            tipo=movimentacao.tipo.value,
            quantidade=movimentacao.quantidade,
            validade=movimentacao.validade,
            valor_unitario=movimentacao.valor_unitario,
            motivo=movimentacao.motivo,
            usuario_id=movimentacao.usuario_id,
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return self._para_entidade(modelo)

    def buscar_por_id(self, movimentacao_id: UUID) -> Movimentacao | None:
        modelo = self.db.query(MovimentacaoModel).filter(
            MovimentacaoModel.id == movimentacao_id
        ).first()
        return self._para_entidade(modelo) if modelo else None

    def listar_por_produto(self, produto_id: UUID) -> list[Movimentacao]:
        modelos = self.db.query(MovimentacaoModel).filter(
            MovimentacaoModel.produto_id == produto_id
        ).order_by(MovimentacaoModel.criado_em.desc()).all()
        return [self._para_entidade(m) for m in modelos]

    def _para_entidade(self, modelo: MovimentacaoModel) -> Movimentacao:
        return Movimentacao(
            id=modelo.id,
            produto_id=modelo.produto_id,
            localizacao=Localizacao(modelo.localizacao),
            tipo=TipoMovimentacao(modelo.tipo),
            quantidade=modelo.quantidade,
            validade=modelo.validade,
            valor_unitario=modelo.valor_unitario,
            motivo=modelo.motivo,
            usuario_id=modelo.usuario_id,
            criado_em=modelo.criado_em,
        )