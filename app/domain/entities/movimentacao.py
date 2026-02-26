from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class TipoMovimentacao(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE_ENTRADA = "AJUSTE_ENTRADA"
    AJUSTE_SAIDA = "AJUSTE_SAIDA"


class Localizacao(str, Enum):
    LOJA = "LOJA"
    GALPAO = "GALPAO"


@dataclass
class Movimentacao:
    produto_id: UUID
    localizacao: Localizacao
    tipo: TipoMovimentacao
    quantidade: Decimal
    usuario_id: UUID
    id: UUID = field(default_factory=uuid4)
    validade: date | None = None
    valor_unitario: Decimal | None = None
    motivo: str | None = None
    criado_em: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self._validar_quantidade()
        self._validar_motivo()

    def _validar_quantidade(self) -> None:
        """Quantidade sempre positiva — a direção é definida pelo tipo."""
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")

    def _validar_motivo(self) -> None:
        """Motivo obrigatório para ajustes."""
        tipos_ajuste = {TipoMovimentacao.AJUSTE_ENTRADA, TipoMovimentacao.AJUSTE_SAIDA}
        if self.tipo in tipos_ajuste and not self.motivo:
            raise ValueError(
                "Motivo é obrigatório para movimentações do tipo AJUSTE."
            )