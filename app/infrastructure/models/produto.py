import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base


class ProdutoModel(Base):
    __tablename__ = "produto"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    ncm: Mapped[str | None] = mapped_column(String(8), nullable=True)
    unidade_comercial: Mapped[str] = mapped_column(String(10), nullable=False)
    requer_validade: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    estoque_minimo: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relacionamento com fornecedores via tabela intermediária
    fornecedores: Mapped[list["ProdutoFornecedorModel"]] = relationship(
        back_populates="produto"
    )

    # Relacionamento com registros de estoque
    estoques: Mapped[list["EstoqueModel"]] = relationship(
        back_populates="produto"
    )

    # Relacionamento com movimentações
    movimentacoes: Mapped[list["MovimentacaoModel"]] = relationship(
        back_populates="produto"
    )