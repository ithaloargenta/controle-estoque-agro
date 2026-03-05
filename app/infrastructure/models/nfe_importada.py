import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.connection import Base


class NfeImportadaModel(Base):
    __tablename__ = "nfe_importada"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chave_acesso: Mapped[str] = mapped_column(String(44), unique=True, nullable=False)
    fornecedor_cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )