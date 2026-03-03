from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class ItemSazonalidade:
    ncm_prefixo: str
    descricao_ncm: str
    dados_mensais: dict[str, Decimal]


@dataclass
class RelatorioSazonalidadeInput:
    ano: int


class RelatorioSazonalidade:
    def __init__(self, db):
        self.db = db

    def executar(self, input: RelatorioSazonalidadeInput) -> list[ItemSazonalidade]:
        from sqlalchemy import func, extract
        from app.infrastructure.models.movimentacao import MovimentacaoModel
        from app.infrastructure.models.produto import ProdutoModel
        from app.infrastructure.models.ncm_regra import NcmRegraModel

        tipos_saida = ('SAIDA', 'AJUSTE_SAIDA')

        resultados = (
            self.db.query(
                func.substr(ProdutoModel.ncm, 1, 4).label("ncm_prefixo"),
                extract('month', MovimentacaoModel.criado_em).label("mes"),
                func.sum(MovimentacaoModel.quantidade).label("total")
            )
            .join(ProdutoModel, MovimentacaoModel.produto_id == ProdutoModel.id)
            .filter(MovimentacaoModel.tipo.in_(tipos_saida))
            .filter(extract('year', MovimentacaoModel.criado_em) == input.ano)
            .filter(ProdutoModel.ncm != None)
            .group_by(
                func.substr(ProdutoModel.ncm, 1, 4),
                extract('month', MovimentacaoModel.criado_em)
            )
            .all()
        )

        if not resultados:
            return []

        # Busca descrições dos NCMs
        ncm_prefixos = list({r.ncm_prefixo for r in resultados})
        regras = (
            self.db.query(NcmRegraModel)
            .filter(NcmRegraModel.ncm_prefixo.in_(ncm_prefixos))
            .all()
        )
        regras_map = {r.ncm_prefixo: r.descricao for r in regras}

        meses_nomes = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }

        # Agrupa por NCM
        dados: dict[str, dict] = {}
        for r in resultados:
            ncm = r.ncm_prefixo
            if ncm not in dados:
                dados[ncm] = {mes: Decimal("0") for mes in meses_nomes.values()}
            dados[ncm][meses_nomes[int(r.mes)]] = r.total

        return [
            ItemSazonalidade(
                ncm_prefixo=ncm,
                descricao_ncm=regras_map.get(ncm, "NCM não mapeado"),
                dados_mensais=meses,
            )
            for ncm, meses in dados.items()
        ]