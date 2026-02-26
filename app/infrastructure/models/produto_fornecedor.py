import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base


class ProdutoFornecedorModel(Base):
    __tablename__ = "produto_fornecedor"

    __table_args__ = (
        # Garante que a combinação produto + fornecedor seja única
        UniqueConstraint("produto_id", "fornecedor_id", name="uq_produto_fornecedor"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("produto.id"), nullable=False
    )
    fornecedor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fornecedor.id"), nullable=False
    )
    codigo_fornecedor: Mapped[str | None] = mapped_column(
        String(60), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relacionamentos
    produto: Mapped["ProdutoModel"] = relationship(
        back_populates="fornecedores"
    )
    fornecedor: Mapped["FornecedorModel"] = relationship(
        back_populates="produtos"
    )