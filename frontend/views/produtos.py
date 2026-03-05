import streamlit as st
import pandas as pd
from services.api import get, post
from services.api import patch


def render():
    st.title("🛒 Produtos")

    aba = st.tabs(["Lista de produtos", "Cadastrar produto"])

    # --- Aba 1: Lista ---
    with aba[0]:
        produtos = get("/produtos/") or []

        if not produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            busca = st.text_input("🔍 Buscar", placeholder="Digite parte do nome ou NCM...")

            if busca:
                produtos = [
                    p for p in produtos
                    if busca.lower() in p["descricao"].lower()
                    or busca in (p.get("ncm") or "")
                ]

            st.markdown(f"**{len(produtos)} produto(s) encontrado(s)**")

            for produto in produtos:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([4, 1, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{produto['descricao']}**")
                        ncm = produto.get("ncm") or "—"
                        st.caption(f"NCM: {ncm} | Unidade: {produto['unidade_comercial']} | Estoque mín.: {produto['estoque_minimo']}")
                    with col2:
                        validade = "✅ Sim" if produto.get("requer_validade") else "❌ Não"
                        st.caption("Validade")
                        st.markdown(validade)
                    with col3:
                        ativo = "✅ Ativo" if produto.get("ativo") else "❌ Inativo"
                        st.caption("Status")
                        st.markdown(ativo)
                    with col4:
                        st.caption(" ")
                        if produto.get("ativo"):
                            if st.button("Desativar", key=f"des_{produto['id']}", use_container_width=True):
                                st.session_state[f"confirmar_desativar_{produto['id']}"] = True

                    with col5:
                        st.caption(" ")

                    # Confirmação de desativação
                    if st.session_state.get(f"confirmar_desativar_{produto['id']}"):
                        st.warning(f"Tem certeza que deseja desativar **{produto['descricao']}**?")
                        col_sim, col_nao = st.columns(2)
                        with col_sim:
                            if st.button("✅ Confirmar", key=f"conf_{produto['id']}", type="primary"):
                                resultado = patch(f"/produtos/{produto['id']}/desativar")
                                if resultado:
                                    st.success(resultado.get("mensagem", "Produto desativado."))
                                    del st.session_state[f"confirmar_desativar_{produto['id']}"]
                                    st.rerun()
                        with col_nao:
                            if st.button("❌ Cancelar", key=f"canc_{produto['id']}"):
                                del st.session_state[f"confirmar_desativar_{produto['id']}"]
                                st.rerun()

                st.divider()

    # --- Aba 2: Cadastrar ---
    with aba[1]:
        st.markdown("### Novo produto")

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

        if ncm and len(ncm) >= 4:
            st.info(f"O estoque mínimo será calculado automaticamente pelo NCM {ncm[:4]}. Altere acima apenas se necessário.")

        if st.button("Cadastrar produto", type="primary", use_container_width=True):
            if not descricao:
                st.error("A descrição é obrigatória.")
            else:
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