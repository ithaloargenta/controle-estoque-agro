from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass
class Produto:
    descricao: str
    unidade_comercial: str
    id: UUID = field(default_factory=uuid4)
    ncm: str | None = None
    requer_validade: bool = False
    ativo: bool = True
    estoque_minimo: int = 2
    criado_em: datetime = field(default_factory=datetime.now)

    def validar_validade_para_movimentacao(self, validade: date | None) -> None:
        """
        Regra de negócio: se o produto requer validade,
        toda movimentação deve informar a data de validade.
        """
        if self.requer_validade and validade is None:
            raise ValueError(
                f"O produto '{self.descricao}' requer informação de validade."
            )