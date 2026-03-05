import streamlit as st
from services.api import get, post


def render():
    st.title("🔧 Ajuste de estoque")

    estoque = get("/estoque/enriquecido") or []
    produtos = {item["descricao"]: item for item in estoque}

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    col1, col2 = st.columns(2)

    with col1:
        produto_nome = st.selectbox("Produto", options=list(produtos.keys()))

    produto = produtos.get(produto_nome)
    estoque_atual = float(produto["quantidade"]) if produto else 0

    with col2:
        tipo = st.selectbox("Tipo de ajuste", options=["AJUSTE_ENTRADA", "AJUSTE_SAIDA"],
                            format_func=lambda x: "➕ Ajuste de entrada" if x == "AJUSTE_ENTRADA" else "➖ Ajuste de saída")

    st.markdown(f"**Estoque atual:** {estoque_atual:.3f} {produto['unidade_comercial']}")

    col3, col4 = st.columns(2)

    with col3:
        max_val = estoque_atual if tipo == "AJUSTE_SAIDA" else 999999.0
        quantidade = st.number_input(
            "Quantidade",
            min_value=0.001,
            max_value=max_val,
            step=0.001,
            format="%.3f"
        )

    with col4:
        motivo = st.text_input("Motivo (obrigatório)", placeholder="Ex: Perda por vencimento, Correção de inventário...")

    validade = None
    if st.checkbox("Informar validade"):
        validade = st.date_input("Validade")

    if st.button("Revisar ajuste", type="primary", use_container_width=True):
        if not motivo:
            st.error("O motivo é obrigatório para ajustes.")
        else:
            if tipo == "AJUSTE_ENTRADA":
                estoque_apos = estoque_atual + quantidade
            else:
                estoque_apos = estoque_atual - quantidade

            st.session_state["ajuste_revisao"] = {
                "produto_id": produto["produto_id"],
                "produto_nome": produto_nome,
                "localizacao": produto["localizacao"],
                "tipo": tipo,
                "quantidade": quantidade,
                "motivo": motivo,
                "validade": validade.isoformat() if validade else None,
                "estoque_atual": estoque_atual,
                "estoque_apos": estoque_apos,
                "unidade": produto["unidade_comercial"],
            }

    if "ajuste_revisao" in st.session_state:
        r = st.session_state["ajuste_revisao"]
        st.markdown("---")
        st.markdown("### Confirmar ajuste")
        tipo_label = "Ajuste de entrada" if r["tipo"] == "AJUSTE_ENTRADA" else "Ajuste de saída"
        st.markdown(f"**Produto:** {r['produto_nome']}")
        st.markdown(f"**Tipo:** {tipo_label}")
        st.markdown(f"**Quantidade:** {r['quantidade']:.3f} {r['unidade']}")
        st.markdown(f"**Motivo:** {r['motivo']}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estoque atual", f"{r['estoque_atual']:.3f}")
        with col2:
            delta = r["quantidade"] if r["tipo"] == "AJUSTE_ENTRADA" else -r["quantidade"]
            st.metric("Estoque após ajuste", f"{r['estoque_apos']:.3f}", delta=f"{delta:.3f}")

        col_sim, col_nao = st.columns(2)
        with col_sim:
            if st.button("✅ Confirmar ajuste", type="primary", use_container_width=True):
                resultado = post("/movimentacoes/", data={
                    "produto_id": r["produto_id"],
                    "localizacao": r["localizacao"],
                    "tipo": r["tipo"],
                    "quantidade": r["quantidade"],
                    "motivo": r["motivo"],
                    "validade": r["validade"],
                })
                if resultado:
                    st.success("Ajuste registrado com sucesso!")
                    del st.session_state["ajuste_revisao"]
                    st.rerun()
        with col_nao:
            if st.button("❌ Cancelar", use_container_width=True):
                del st.session_state["ajuste_revisao"]
                st.rerun()