from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.fornecedor import Fornecedor
from app.domain.repositories.fornecedor_repository import FornecedorRepository


@dataclass
class CadastrarFornecedorInput:
    razao_social: str
    cnpj: str | None = None


@dataclass
class CadastrarFornecedorOutput:
    id: UUID
    razao_social: str
    cnpj: str | None
    ativo: bool


class CadastrarFornecedor:
    def __init__(self, fornecedor_repository: FornecedorRepository):
        self.fornecedor_repository = fornecedor_repository

    def executar(self, input: CadastrarFornecedorInput) -> CadastrarFornecedorOutput:
        # Verifica duplicidade de CNPJ antes de cadastrar
        if input.cnpj:
            existente = self.fornecedor_repository.buscar_por_cnpj(input.cnpj)
            if existente:
                raise ValueError(
                    f"Já existe um fornecedor cadastrado com o CNPJ {input.cnpj}."
                )

        fornecedor = Fornecedor(
            razao_social=input.razao_social,
            cnpj=input.cnpj,
        )

        fornecedor_salvo = self.fornecedor_repository.salvar(fornecedor)

        return CadastrarFornecedorOutput(
            id=fornecedor_salvo.id,
            razao_social=fornecedor_salvo.razao_social,
            cnpj=fornecedor_salvo.cnpj,
            ativo=fornecedor_salvo.ativo,
        )