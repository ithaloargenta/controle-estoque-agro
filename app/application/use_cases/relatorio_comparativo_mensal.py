from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class MesComparativo:
    entradas: Decimal
    saidas: Decimal
    valor_entradas: Decimal


@dataclass
class ItemComparativoMensal:
    produto_id: UUID
    descricao: str
    ncm: str | None
    unidade_comercial: str
    mes_1: MesComparativo
    mes_2: MesComparativo
    variacao_entradas: float | None
    variacao_saidas: float | None


@dataclass
class RelatorioComparativoMensalInput:
    ano_mes_1: str  # formato YYYY-MM
    ano_mes_2: str  # formato YYYY-MM


class RelatorioComparativoMensal:
    def __init__(self, db):
        self.db = db

    def _parsear_mes(self, ano_mes: str) -> tuple[date, date]:
        from calendar import monthrange
        ano, mes = int(ano_mes.split("-")[0]), int(ano_mes.split("-")[1])
        inicio = date(ano, mes, 1)
        fim = date(ano, mes, monthrange(ano, mes)[1])
        return inicio, fim

    def _buscar_dados_mes(self, inicio: date, fim: date) -> dict[UUID, dict]:
        from app.infrastructure.models.movimentacao import MovimentacaoModel

        movimentacoes = (
            self.db.query(MovimentacaoModel)
            .filter(MovimentacaoModel.criado_em >= inicio)
            .filter(MovimentacaoModel.criado_em <= fim)
            .all()
        )

        dados: dict[UUID, dict] = {}
        for mov in movimentacoes:
            if mov.produto_id not in dados:
                dados[mov.produto_id] = {
                    "entradas": Decimal("0"),
                    "saidas": Decimal("0"),
                    "valor_entradas": Decimal("0"),
                }

            if mov.tipo in ('ENTRADA', 'AJUSTE_ENTRADA'):
                dados[mov.produto_id]["entradas"] += mov.quantidade
                if mov.valor_unitario:
                    dados[mov.produto_id]["valor_entradas"] += mov.quantidade * mov.valor_unitario
            elif mov.tipo in ('SAIDA', 'AJUSTE_SAIDA'):
                dados[mov.produto_id]["saidas"] += mov.quantidade

        return dados

    def executar(self, input: RelatorioComparativoMensalInput) -> list[ItemComparativoMensal]:
        from app.infrastructure.models.produto import ProdutoModel

        inicio_1, fim_1 = self._parsear_mes(input.ano_mes_1)
        inicio_2, fim_2 = self._parsear_mes(input.ano_mes_2)

        dados_1 = self._buscar_dados_mes(inicio_1, fim_1)
        dados_2 = self._buscar_dados_mes(inicio_2, fim_2)

        todos_ids = set(dados_1.keys()) | set(dados_2.keys())

        if not todos_ids:
            return []

        produtos = (
            self.db.query(ProdutoModel)
            .filter(ProdutoModel.id.in_(todos_ids))
            .all()
        )
        produtos_map = {p.id: p for p in produtos}

        zero = {"entradas": Decimal("0"), "saidas": Decimal("0"), "valor_entradas": Decimal("0")}

        itens = []
        for produto_id in todos_ids:
            produto = produtos_map.get(produto_id)
            if not produto:
                continue

            d1 = dados_1.get(produto_id, zero)
            d2 = dados_2.get(produto_id, zero)

            def variacao(v1, v2):
                if v1 > 0:
                    return round(float((v2 - v1) / v1 * 100), 2)
                return None

            itens.append(ItemComparativoMensal(
                produto_id=produto_id,
                descricao=produto.descricao,
                ncm=produto.ncm,
                unidade_comercial=produto.unidade_comercial,
                mes_1=MesComparativo(
                    entradas=d1["entradas"],
                    saidas=d1["saidas"],
                    valor_entradas=d1["valor_entradas"],
                ),
                mes_2=MesComparativo(
                    entradas=d2["entradas"],
                    saidas=d2["saidas"],
                    valor_entradas=d2["valor_entradas"],
                ),
                variacao_entradas=variacao(d1["entradas"], d2["entradas"]),
                variacao_saidas=variacao(d1["saidas"], d2["saidas"]),
            ))

        return sorted(itens, key=lambda x: x.descricao)