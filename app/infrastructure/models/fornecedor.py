import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base


class FornecedorModel(Base):
    __tablename__ = "fornecedor"

    __table_args__ = (
        # Garante que o CNPJ tenha exatamente 14 dígitos numéricos
        CheckConstraint(r"cnpj ~ '^\d{14}$'", name="ck_fornecedor_cnpj_numerico"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    razao_social: Mapped[str] = mapped_column(String(150), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relacionamento com produtos via tabela intermediária
    produtos: Mapped[list["ProdutoFornecedorModel"]] = relationship(
        back_populates="fornecedor"
    )