from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.estoque import Estoque
from app.domain.repositories.estoque_repository import EstoqueRepository
from app.infrastructure.models.estoque import EstoqueModel


class EstoqueRepositoryImpl(EstoqueRepository):
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_produto(self, produto_id: UUID) -> list[Estoque]:
        modelos = self.db.query(EstoqueModel).filter(
            EstoqueModel.produto_id == produto_id
        ).all()
        return [self._para_entidade(m) for m in modelos]

    def buscar_por_produto_localizacao_validade(
        self,
        produto_id: UUID,
        localizacao: str,
        validade: date | None,
    ) -> Estoque | None:
        query = self.db.query(EstoqueModel).filter(
            EstoqueModel.produto_id == produto_id,
            EstoqueModel.localizacao == localizacao,
        )

        # Tratamento correto de NULL para validade
        if validade is None:
            query = query.filter(EstoqueModel.validade.is_(None))
        else:
            query = query.filter(EstoqueModel.validade == validade)

        modelo = query.first()
        return self._para_entidade(modelo) if modelo else None

    def listar_todos(self) -> list[Estoque]:
        modelos = self.db.query(EstoqueModel).all()
        return [self._para_entidade(m) for m in modelos]

    def _para_entidade(self, modelo: EstoqueModel) -> Estoque:
        return Estoque(
            id=modelo.id,
            produto_id=modelo.produto_id,
            localizacao=modelo.localizacao,
            quantidade=modelo.quantidade,
            validade=modelo.validade,
            atualizado_em=modelo.atualizado_em,
        )