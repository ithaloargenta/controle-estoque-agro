import streamlit as st
from services.api import post


def render():
    st.title("🛒 Cadastrar produto")

    col1, col2 = st.columns(2)

    with col1:
        descricao = st.text_input("Descrição", placeholder="Nome completo do produto")
        ncm = st.text_input("NCM", placeholder="Ex: 30021590", max_chars=8)
        unidade_comercial = st.selectbox(
            "Unidade comercial",
            options=["UN", "KG", "L", "M", "CX", "PCT", "PAR", "MT", "SC", "FD"],
        )

    with col2:
        requer_validade = st.checkbox("Produto com validade (medicamentos, vacinas...)")
        estoque_minimo = st.number_input(
            "Estoque mínimo",
            min_value=0,
            value=2,
            help="Deixe como está para usar o valor automático pelo NCM",
        )
        localizacao = st.selectbox("Localização padrão", options=["LOJA", "GALPAO"])

    if ncm and len(ncm) >= 4:
        st.info(f"O estoque mínimo será calculado automaticamente pelo NCM {ncm[:4]}. Altere acima apenas se necessário.")

    if st.button("Cadastrar produto", type="primary", use_container_width=True):
        if not descricao:
            st.error("A descrição é obrigatória.")
            return

        resultado = post("/produtos/", data={
            "descricao": descricao,
            "ncm": ncm if ncm else None,
            "unidade_comercial": unidade_comercial,
            "requer_validade": requer_validade,
            "estoque_minimo": estoque_minimo,
        })

        if resultado:
            st.success(f"Produto **{descricao}** cadastrado com sucesso!")
            st.markdown(f"**Estoque mínimo definido:** {resultado.get('estoque_minimo', estoque_minimo)}")
            st.markdown(f"**ID:** `{resultado.get('id')}`")