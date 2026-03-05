import streamlit as st
import pandas as pd
from services.api import get, put


def render():
    st.title("⚙️ Configurações")

    st.markdown("### Regras de estoque mínimo por NCM")
    st.markdown("Esses valores são usados automaticamente ao cadastrar novos produtos pelo NCM.")

    regras = get("/ncm-regras/") or []

    if not regras:
        st.info("Nenhuma regra de NCM encontrada.")
        return

    # Busca
    busca = st.text_input("🔍 Buscar", placeholder="Digite NCM ou descrição...")
    if busca:
        regras = [r for r in regras if busca.lower() in r["descricao"].lower() or busca in r["ncm_prefixo"]]

    st.markdown(f"**{len(regras)} regra(s) encontrada(s)**")

    # Tabela de visualização
    df = pd.DataFrame(regras)[["ncm_prefixo", "descricao", "estoque_minimo"]]
    df.columns = ["NCM", "Descrição", "Estoque mínimo"]
    st.dataframe(df, use_container_width=True, hide_index=True, height=350)

    st.markdown("---")
    st.markdown("### Editar regra")

    regras_map = {f"{r['ncm_prefixo']} — {r['descricao']}": r for r in regras}
    ncm_selecionado = st.selectbox("Selecione o NCM para editar", options=list(regras_map.keys()))
    regra = regras_map[ncm_selecionado]

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("NCM", value=regra["ncm_prefixo"], disabled=True)
        st.text_input("Descrição", value=regra["descricao"], disabled=True)
    with col2:
        novo_minimo = st.number_input(
            "Novo estoque mínimo",
            min_value=0,
            value=int(regra["estoque_minimo"]),
        )

    if st.button("Salvar alteração", type="primary", use_container_width=True):
        resultado = put(f"/ncm-regras/{regra['id']}", data={"estoque_minimo": novo_minimo})
        if resultado:
            st.success(f"Regra do NCM {regra['ncm_prefixo']} atualizada — novo mínimo: {novo_minimo}")
            st.rerun()