from uuid import UUID
from app.domain.entities.fornecedor import Fornecedor
from app.domain.repositories.fornecedor_repository import FornecedorRepository


class FornecedorRepositoryFake(FornecedorRepository):
    def __init__(self):
        self._dados: dict[UUID, Fornecedor] = {}

    def salvar(self, fornecedor: Fornecedor) -> Fornecedor:
        self._dados[fornecedor.id] = fornecedor
        return fornecedor

    def buscar_por_id(self, fornecedor_id: UUID) -> Fornecedor | None:
        return self._dados.get(fornecedor_id)

    def buscar_por_cnpj(self, cnpj: str) -> Fornecedor | None:
        for f in self._dados.values():
            if f.cnpj == cnpj:
                return f
        return None

    def listar_ativos(self) -> list[Fornecedor]:
        return [f for f in self._dados.values() if f.ativo]