import streamlit as st
import pandas as pd
from services.api import get


def render():
    st.title("📦 Estoque")

    dados = get("/estoque/enriquecido") or []

    if not dados:
        st.info("Nenhum produto em estoque.")
        return

    df = pd.DataFrame(dados)

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        busca = st.text_input("🔍 Buscar produto", placeholder="Digite parte do nome...")
    with col2:
        apenas_abaixo = st.checkbox("Mostrar apenas abaixo do mínimo")

    if busca:
        df = df[df["descricao"].str.contains(busca, case=False, na=False)]

    if apenas_abaixo:
        df = df[df["abaixo_do_minimo"] == True]

    # Formata tabela
    df_exibir = df[["descricao", "ncm", "unidade_comercial", "localizacao", "quantidade", "estoque_minimo", "abaixo_do_minimo", "validade"]].copy()
    df_exibir.columns = ["Produto", "NCM", "Unidade", "Local", "Quantidade", "Mínimo", "Abaixo do mínimo", "Validade"]
    df_exibir["Quantidade"] = df_exibir["Quantidade"].apply(lambda x: f"{float(x):.3f}")
    df_exibir["Abaixo do mínimo"] = df_exibir["Abaixo do mínimo"].apply(lambda x: "⚠️ Sim" if x else "✅ Não")

    st.markdown(f"**{len(df_exibir)} registro(s) encontrado(s)**")
    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True,
        height=600,
    )