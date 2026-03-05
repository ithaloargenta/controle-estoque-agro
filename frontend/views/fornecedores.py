import streamlit as st
import pandas as pd
from services.api import get, post


def render():
    st.title("🏭 Fornecedores")

    aba = st.tabs(["Lista de fornecedores", "Cadastrar fornecedor", "Vincular a produto"])

    # --- Aba 1: Lista ---
    with aba[0]:
        fornecedores = get("/fornecedores/") or []
        if not fornecedores:
            st.info("Nenhum fornecedor cadastrado.")
        else:
            df = pd.DataFrame(fornecedores)[["razao_social", "cnpj", "ativo"]]
            df.columns = ["Razão social", "CNPJ", "Ativo"]
            df["Ativo"] = df["Ativo"].apply(lambda x: "✅ Sim" if x else "❌ Não")
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- Aba 2: Cadastrar ---
    with aba[1]:
        st.markdown("### Novo fornecedor")
        col1, col2 = st.columns(2)
        with col1:
            razao_social = st.text_input("Razão social", placeholder="Nome da empresa")
        with col2:
            cnpj = st.text_input("CNPJ", placeholder="00000000000000", max_chars=14)

        if st.button("Cadastrar fornecedor", type="primary", use_container_width=True):
            if not razao_social or not cnpj:
                st.error("Razão social e CNPJ são obrigatórios.")
            elif len(cnpj) != 14:
                st.error("CNPJ deve ter 14 dígitos sem pontuação.")
            else:
                resultado = post("/fornecedores/", data={
                    "razao_social": razao_social,
                    "cnpj": cnpj,
                })
                if resultado:
                    st.success(f"Fornecedor **{razao_social}** cadastrado com sucesso!")

    # --- Aba 3: Vincular ---
    with aba[2]:
        st.markdown("### Vincular fornecedor a produto")

        fornecedores = get("/fornecedores/") or []
        estoque = get("/estoque/enriquecido") or []

        if not fornecedores or not estoque:
            st.info("Cadastre fornecedores e produtos antes de vincular.")
            return

        fornecedores_map = {f["razao_social"]: f["id"] for f in fornecedores}
        produtos_map = {item["descricao"]: item["produto_id"] for item in estoque}

        col1, col2 = st.columns(2)
        with col1:
            fornecedor_nome = st.selectbox("Fornecedor", options=list(fornecedores_map.keys()))
        with col2:
            produto_nome = st.selectbox("Produto", options=list(produtos_map.keys()))

        codigo_fornecedor = st.text_input(
            "Código do produto no fornecedor (opcional)",
            placeholder="Ex: SKU-12345"
        )

        if st.button("Vincular", type="primary", use_container_width=True):
            fornecedor_id = fornecedores_map[fornecedor_nome]
            produto_id = produtos_map[produto_nome]

            resultado = post(f"/fornecedores/{fornecedor_id}/produtos", data={
                "produto_id": produto_id,
                "codigo_fornecedor": codigo_fornecedor if codigo_fornecedor else None,
            })
            if resultado:
                st.success(f"**{produto_nome}** vinculado a **{fornecedor_nome}** com sucesso!")