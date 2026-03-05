import streamlit as st
import pandas as pd
from services.api import post


def render():
    st.title("📥 Importar NF-e")

    st.markdown("Faça o upload do XML da nota fiscal de entrada. O sistema vai identificar o fornecedor automaticamente e registrar as movimentações.")

    col1, col2 = st.columns([2, 1])

    with col1:
        arquivo = st.file_uploader("Selecione o arquivo XML", type=["xml"])

    with col2:
        localizacao = st.selectbox("Localização de destino", options=["LOJA", "GALPAO"])

    if arquivo and st.button("Importar NF-e", type="primary", use_container_width=True):
        with st.spinner("Processando XML..."):
            resultado = post(
                "/importacao/nfe",
                files={"arquivo": (arquivo.name, arquivo.read(), "text/xml")},
                params={"localizacao": localizacao},
            )

        if resultado:
            # Resumo
            st.markdown("---")
            st.markdown("### ✅ Importação concluída")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Produtos criados", resultado["produtos_criados"])
            with col2:
                st.metric("Produtos existentes", resultado["produtos_existentes"])
            with col3:
                st.metric("Movimentações geradas", resultado["movimentacoes_geradas"])
            with col4:
                fornecedor_status = "✅ Novo" if resultado["fornecedor_criado"] else "🔄 Existente"
                st.metric("Fornecedor", fornecedor_status)

            if resultado.get("fornecedor_nome"):
                st.info(f"Fornecedor: **{resultado['fornecedor_nome']}**")

            st.markdown("### Detalhes")
            for detalhe in resultado["detalhes"]:
                if "criado" in detalhe.lower():
                    st.success(detalhe)
                elif "existente" in detalhe.lower():
                    st.info(detalhe)
                else:
                    st.error(detalhe)