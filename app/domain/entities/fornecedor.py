from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Fornecedor:
    razao_social: str
    id: UUID = field(default_factory=uuid4)
    cnpj: str | None = None
    ativo: bool = True
    criado_em: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.cnpj is not None:
            self.validar_cnpj()

    def validar_cnpj(self) -> None:
        if not self.cnpj:
            return
        if not self.cnpj.isdigit():
            raise ValueError("CNPJ deve conter apenas dígitos.")
        if len(self.cnpj) != 14:
            raise ValueError("CNPJ deve conter exatamente 14 dígitos.")