from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository
from app.infrastructure.models.produto import ProdutoModel
from app.infrastructure.models.ncm_regra import NcmRegraModel

ESTOQUE_MINIMO_PADRAO = 2


class ProdutoRepositoryImpl(ProdutoRepository):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, produto: Produto) -> Produto:
        modelo = self.db.query(ProdutoModel).filter(
            ProdutoModel.id == produto.id
        ).first()

        if modelo:
            modelo.descricao = produto.descricao
            modelo.unidade_comercial = produto.unidade_comercial
            modelo.ncm = produto.ncm
            modelo.requer_validade = produto.requer_validade
            modelo.ativo = produto.ativo
            modelo.estoque_minimo = produto.estoque_minimo
        else:
            estoque_minimo = self._calcular_estoque_minimo(produto.ncm, produto.estoque_minimo)
            modelo = ProdutoModel(
                id=produto.id,
                descricao=produto.descricao,
                unidade_comercial=produto.unidade_comercial,
                ncm=produto.ncm,
                requer_validade=produto.requer_validade,
                ativo=produto.ativo,
                estoque_minimo=estoque_minimo,
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

    def _calcular_estoque_minimo(self, ncm: str | None, estoque_minimo_informado: int) -> int:
        # Se o usuário definiu um valor diferente do padrão, respeita
        if estoque_minimo_informado != ESTOQUE_MINIMO_PADRAO:
            return estoque_minimo_informado

        # Se não tem NCM, usa o padrão
        if not ncm:
            return ESTOQUE_MINIMO_PADRAO

        # Busca regra pelo prefixo do NCM (primeiros 4 dígitos)
        prefixo = ncm[:4]
        regra = self.db.query(NcmRegraModel).filter(
            NcmRegraModel.ncm_prefixo == prefixo
        ).first()

        return regra.estoque_minimo if regra else ESTOQUE_MINIMO_PADRAO

    def _para_entidade(self, modelo: ProdutoModel) -> Produto:
        return Produto(
            id=modelo.id,
            descricao=modelo.descricao,
            unidade_comercial=modelo.unidade_comercial,
            ncm=modelo.ncm,
            requer_validade=modelo.requer_validade,
            ativo=modelo.ativo,
            estoque_minimo=modelo.estoque_minimo,
            criado_em=modelo.criado_em,
        )