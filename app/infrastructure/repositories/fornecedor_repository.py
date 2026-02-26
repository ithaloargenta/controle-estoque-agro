from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.fornecedor import Fornecedor
from app.domain.repositories.fornecedor_repository import FornecedorRepository
from app.infrastructure.models.fornecedor import FornecedorModel


class FornecedorRepositoryImpl(FornecedorRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, fornecedor: Fornecedor) -> Fornecedor:
        modelo = self.db.query(FornecedorModel).filter(
            FornecedorModel.id == fornecedor.id
        ).first()

        if modelo:
            modelo.razao_social = fornecedor.razao_social
            modelo.cnpj = fornecedor.cnpj
            modelo.ativo = fornecedor.ativo
        else:
            modelo = FornecedorModel(
                id=fornecedor.id,
                razao_social=fornecedor.razao_social,
                cnpj=fornecedor.cnpj,
                ativo=fornecedor.ativo,
            )
            self.db.add(modelo)

        self.db.commit()
        self.db.refresh(modelo)
        return self._para_entidade(modelo)

    def buscar_por_id(self, fornecedor_id: UUID) -> Fornecedor | None:
        modelo = self.db.query(FornecedorModel).filter(
            FornecedorModel.id == fornecedor_id
        ).first()
        return self._para_entidade(modelo) if modelo else None

    def buscar_por_cnpj(self, cnpj: str) -> Fornecedor | None:
        modelo = self.db.query(FornecedorModel).filter(
            FornecedorModel.cnpj == cnpj
        ).first()
        return self._para_entidade(modelo) if modelo else None

    def listar_ativos(self) -> list[Fornecedor]:
        modelos = self.db.query(FornecedorModel).filter(
            FornecedorModel.ativo == True
        ).all()
        return [self._para_entidade(m) for m in modelos]

    def _para_entidade(self, modelo: FornecedorModel) -> Fornecedor:
        return Fornecedor(
            id=modelo.id,
            razao_social=modelo.razao_social,
            cnpj=modelo.cnpj,
            ativo=modelo.ativo,
            criado_em=modelo.criado_em,
        )