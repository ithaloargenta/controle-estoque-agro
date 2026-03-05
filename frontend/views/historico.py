import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
from services.api import get


TIPOS = {
    "Todos": None,
    "Entrada": "ENTRADA",
    "Saída": "SAIDA",
    "Ajuste de entrada": "AJUSTE_ENTRADA",
    "Ajuste de saída": "AJUSTE_SAIDA",
}

TIPO_LABELS = {
    "ENTRADA": "📥 Entrada",
    "SAIDA": "📤 Saída",
    "AJUSTE_ENTRADA": "➕ Ajuste entrada",
    "AJUSTE_SAIDA": "➖ Ajuste saída",
}


def exportar_excel(df: pd.DataFrame):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Histórico")
    return buffer.getvalue()


def render():
    st.title("📋 Histórico de movimentações")

    # Filtros
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    with col1:
        data_inicio = st.date_input(
            "De",
            value=date(date.today().year, date.today().month, 1),
        )
    with col2:
        data_fim = st.date_input("Até", value=date.today())
    with col3:
        tipo_label = st.selectbox("Tipo", options=list(TIPOS.keys()))
    with col4:
        busca_produto = st.text_input("🔍 Produto", placeholder="Digite parte do nome...")

    # Busca
    params = {
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
    }
    tipo_valor = TIPOS[tipo_label]
    if tipo_valor:
        params["tipo"] = tipo_valor

    dados = get("/relatorios/historico", params=params) or []

    # Filtro por produto no frontend
    if busca_produto:
        dados = [d for d in dados if busca_produto.lower() in d["descricao"].lower()]

    if not dados:
        st.info("Nenhuma movimentação encontrada no período.")
        return

    # Limita 50 por vez
    total = len(dados)
    dados_pagina = dados[:50]

    st.markdown(f"**{total} registro(s) encontrado(s)** — exibindo os 50 mais recentes")

    # Monta dataframe
    df = pd.DataFrame([{
        "Data": d["criado_em"][:16].replace("T", " "),
        "Produto": d["descricao"],
        "Tipo": TIPO_LABELS.get(d["tipo"], d["tipo"]),
        "Quantidade": f"{float(d['quantidade']):.3f} {d['unidade_comercial']}",
        "Valor unit.": f"R$ {float(d['valor_unitario']):,.2f}" if d.get("valor_unitario") else "-",
        "Local": d["localizacao"],
        "Motivo": d.get("motivo") or "-",
    } for d in dados_pagina])

    st.dataframe(df, use_container_width=True, hide_index=True, height=500)

    # Exportar
    col_exp, _ = st.columns([1, 3])
    with col_exp:
        df_export = pd.DataFrame([{
            "Data": d["criado_em"][:16].replace("T", " "),
            "Produto": d["descricao"],
            "Tipo": d["tipo"],
            "Quantidade": float(d["quantidade"]),
            "Unidade": d["unidade_comercial"],
            "Valor unitário": float(d["valor_unitario"]) if d.get("valor_unitario") else None,
            "Localização": d["localizacao"],
            "Motivo": d.get("motivo") or "",
        } for d in dados])

        st.download_button(
            label="📥 Exportar Excel",
            data=exportar_excel(df_export),
            file_name=f"historico_{data_inicio}_{data_fim}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )