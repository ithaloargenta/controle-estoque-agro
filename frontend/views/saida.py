import streamlit as st
from services.api import get, post


def render():
    st.title("🔻 Saída")

    # Busca estoque
    estoque = get("/estoque/enriquecido") or []
    itens_com_estoque = [item for item in estoque if float(item["quantidade"]) > 0]
    produtos = {item["descricao"]: item for item in itens_com_estoque}

    if not produtos:
        st.info("Nenhum produto com estoque disponível.")
        return

    col1, col2 = st.columns(2)

    with col1:
        produto_nome = st.selectbox("Produto", options=list(produtos.keys()))

    produto = produtos.get(produto_nome)
    estoque_atual = float(produto["quantidade"]) if produto else 0

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**Estoque atual:** {estoque_atual:.3f} {produto['unidade_comercial']}")

    quantidade = st.number_input(
        "Quantidade",
        min_value=0.001,
        max_value=estoque_atual,
        step=0.001,
        format="%.3f"
    )

    estoque_apos = estoque_atual - quantidade

    if st.button("Revisar saída", type="primary", use_container_width=True):
        st.session_state["saida_revisao"] = {
            "produto_id": produto["produto_id"],
            "produto_nome": produto_nome,
            "localizacao": produto["localizacao"],
            "quantidade": quantidade,
            "estoque_atual": estoque_atual,
            "estoque_apos": estoque_apos,
            "unidade": produto["unidade_comercial"],
        }

    if "saida_revisao" in st.session_state:
        r = st.session_state["saida_revisao"]
        st.markdown("---")
        st.markdown("### Confirmar saída")
        st.markdown(f"**Produto:** {r['produto_nome']}")
        st.markdown(f"**Localização:** {r['localizacao']}")
        st.markdown(f"**Quantidade a baixar:** {r['quantidade']:.3f} {r['unidade']}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estoque atual", f"{r['estoque_atual']:.3f}")
        with col2:
            delta = -r["quantidade"]
            st.metric("Estoque após saída", f"{r['estoque_apos']:.3f}", delta=f"{delta:.3f}")

        col_sim, col_nao = st.columns(2)
        with col_sim:
            if st.button("✅ Confirmar saída", type="primary", use_container_width=True):
                resultado = post("/movimentacoes/", data={
                    "produto_id": r["produto_id"],
                    "localizacao": r["localizacao"],
                    "tipo": "SAIDA",
                    "quantidade": r["quantidade"],
                })
                if resultado:
                    st.success("Saída registrada com sucesso!")
                    del st.session_state["saida_revisao"]
                    st.rerun()
        with col_nao:
            if st.button("❌ Cancelar", use_container_width=True):
                del st.session_state["saida_revisao"]
                st.rerun()