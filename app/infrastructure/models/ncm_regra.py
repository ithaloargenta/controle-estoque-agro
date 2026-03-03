from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.connection import Base


class NcmRegraModel(Base):
    __tablename__ = "ncm_regra"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ncm_prefixo: Mapped[str] = mapped_column(String(8), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    estoque_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )