from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository
from app.infrastructure.models.produto import ProdutoModel


class ProdutoRepositoryImpl(ProdutoRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, produto: Produto) -> Produto:
        modelo = self.db.query(ProdutoModel).filter(
            ProdutoModel.id == produto.id
        ).first()

        if modelo:
            # Atualiza existente
            modelo.descricao = produto.descricao
            modelo.unidade_comercial = produto.unidade_comercial
            modelo.ncm = produto.ncm
            modelo.requer_validade = produto.requer_validade
            modelo.ativo = produto.ativo
        else:
            # Cria novo
            modelo = ProdutoModel(
                id=produto.id,
                descricao=produto.descricao,
                unidade_comercial=produto.unidade_comercial,
                ncm=produto.ncm,
                requer_validade=produto.requer_validade,
                ativo=produto.ativo,
            )
            self.db.add(modelo)

        self.db.commit()
        self.db.refresh(modelo)
        return self._para_entidade(modelo)

    def buscar_por_id(self, produto_id: UUID) -> Produto | None:
        modelo = self.db.query(ProdutoModel).filter(
            ProdutoModel.id == produto_id
        ).first()
        return self._para_entidade(modelo) if modelo else None

    def buscar_por_descricao(self, descricao: str) -> list[Produto]:
        modelos = self.db.query(ProdutoModel).filter(
            ProdutoModel.descricao.ilike(f"%{descricao}%")
        ).all()
        return [self._para_entidade(m) for m in modelos]

    def listar_ativos(self) -> list[Produto]:
        modelos = self.db.query(ProdutoModel).filter(
            ProdutoModel.ativo == True
        ).all()
        return [self._para_entidade(m) for m in modelos]

    def _para_entidade(self, modelo: ProdutoModel) -> Produto:
        return Produto(
            id=modelo.id,
            descricao=modelo.descricao,
            unidade_comercial=modelo.unidade_comercial,
            ncm=modelo.ncm,
            requer_validade=modelo.requer_validade,
            ativo=modelo.ativo,
            criado_em=modelo.criado_em,
        )