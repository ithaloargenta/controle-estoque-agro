import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Date, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base


class LocalizacaoEnum(str, Enum):
    LOJA = "LOJA"
    GALPAO = "GALPAO"


class EstoqueModel(Base):
    __tablename__ = "estoque"

    __table_args__ = (
        # Garante quantidade nunca negativa
        CheckConstraint("quantidade >= 0", name="ck_estoque_quantidade_positiva"),
        # Índice parcial 1: unicidade para registros COM validade
        Index(
            "uq_estoque_com_validade",
            "produto_id", "localizacao", "validade",
            unique=True,
            postgresql_where="validade IS NOT NULL",
        ),
        # Índice parcial 2: unicidade para registros SEM validade
        Index(
            "uq_estoque_sem_validade",
            "produto_id", "localizacao",
            unique=True,
            postgresql_where="validade IS NULL",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("produto.id"), nullable=False
    )
    localizacao: Mapped[LocalizacaoEnum] = mapped_column(
        String(10), nullable=False
    )
    validade: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantidade: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False, default=0
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relacionamento com produto
    produto: Mapped["ProdutoModel"] = relationship(
        back_populates="estoques"
    )