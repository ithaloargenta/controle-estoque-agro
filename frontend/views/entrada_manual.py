import streamlit as st
from services.api import get, post


def render():
    st.title("➕ Entrada manual")

    # Busca produtos
    estoque = get("/estoque/enriquecido") or []
    produtos = {item["descricao"]: item for item in estoque}

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    col1, col2 = st.columns(2)

    with col1:
        produto_nome = st.selectbox("Produto", options=list(produtos.keys()))
    
    produto = produtos.get(produto_nome)

    with col2:
        localizacao = st.selectbox("Localização", ["LOJA", "GALPAO"])

    col3, col4 = st.columns(2)

    with col3:
        quantidade = st.number_input("Quantidade", min_value=0.001, step=0.001, format="%.3f")

    with col4:
        valor_unitario = st.number_input("Valor unitário (R$)", min_value=0.0, step=0.01, format="%.2f")

    requer_validade = produto.get("validade") is not None if produto else False
    validade = None
    if requer_validade or st.checkbox("Informar validade"):
        validade = st.date_input("Validade")

    if st.button("Revisar entrada", type="primary", use_container_width=True):
        st.session_state["entrada_revisao"] = {
            "produto_id": produto["produto_id"],
            "produto_nome": produto_nome,
            "localizacao": localizacao,
            "quantidade": quantidade,
            "valor_unitario": valor_unitario if valor_unitario > 0 else None,
            "validade": validade.isoformat() if validade else None,
        }

    if "entrada_revisao" in st.session_state:
        r = st.session_state["entrada_revisao"]
        st.markdown("---")
        st.markdown("### Confirmar entrada")
        st.markdown(f"**Produto:** {r['produto_nome']}")
        st.markdown(f"**Localização:** {r['localizacao']}")
        st.markdown(f"**Quantidade:** {r['quantidade']:.3f}")
        if r["valor_unitario"]:
            st.markdown(f"**Valor unitário:** R$ {r['valor_unitario']:.2f}")
        if r["validade"]:
            st.markdown(f"**Validade:** {r['validade']}")

        col_sim, col_nao = st.columns(2)
        with col_sim:
            if st.button("✅ Confirmar", type="primary", use_container_width=True):
                resultado = post("/movimentacoes/", data={
                    "produto_id": r["produto_id"],
                    "localizacao": r["localizacao"],
                    "tipo": "ENTRADA",
                    "quantidade": r["quantidade"],
                    "valor_unitario": r["valor_unitario"],
                    "validade": r["validade"],
                })
                if resultado:
                    st.success("Entrada registrada com sucesso!")
                    del st.session_state["entrada_revisao"]
                    st.rerun()
        with col_nao:
            if st.button("❌ Cancelar", use_container_width=True):
                del st.session_state["entrada_revisao"]
                st.rerun()