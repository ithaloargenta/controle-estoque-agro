import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Date, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base


class TipoMovimentacaoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE_ENTRADA = "AJUSTE_ENTRADA"
    AJUSTE_SAIDA = "AJUSTE_SAIDA"


class MovimentacaoModel(Base):
    __tablename__ = "movimentacao"

    __table_args__ = (
        # Quantidade sempre positiva — a direção é definida pelo tipo
        CheckConstraint("quantidade > 0", name="ck_movimentacao_quantidade_positiva"),
        # Motivo obrigatório para ajustes
        CheckConstraint(
            "tipo NOT IN ('AJUSTE_ENTRADA', 'AJUSTE_SAIDA') OR motivo IS NOT NULL",
            name="ck_movimentacao_motivo_ajuste",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("produto.id"), nullable=False
    )
    localizacao: Mapped[str] = mapped_column(String(10), nullable=False)
    validade: Mapped[date | None] = mapped_column(Date, nullable=True)
    tipo: Mapped[TipoMovimentacaoEnum] = mapped_column(String(20), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    valor_unitario: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuario.id"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relacionamentos
    produto: Mapped["ProdutoModel"] = relationship(
        back_populates="movimentacoes"
    )
    usuario: Mapped["UsuarioModel"] = relationship(
        back_populates="movimentacoes"
    )