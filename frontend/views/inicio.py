import streamlit as st
import pandas as pd
from datetime import date
from services.api import get


def render():
    st.title("🏠 Início")

    # Busca dados para os cartões
    reposicao = get("/relatorios/reposicao") or []
    vencimento = get("/relatorios/vencimento", params={"dias": 30}) or []
    valor_estoque = get("/relatorios/valor-estoque")
    hoje = date.today()
    giro = get("/relatorios/giro", params={
        "data_inicio": date(hoje.year, hoje.month, 1).isoformat(),
        "data_fim": hoje.isoformat(),
    }) or []

    # Calcula total de saídas do mês
    total_saidas = sum(float(item["quantidade_saida"]) for item in giro)
    valor_total_estoque = float(valor_estoque["valor_total_geral"]) if valor_estoque else 0

    # Cartões de resumo
    st.markdown("### Resumo do dia")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Saídas do mês</div>
            <div class="metric-value">{total_saidas:.0f}</div>
            <div class="metric-label">unidades</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        cor = "critico" if len(reposicao) > 0 else "metric-card"
        st.markdown(f"""
        <div class="{cor}">
            <div class="metric-label">Precisam de reposição</div>
            <div class="metric-value">{len(reposicao)}</div>
            <div class="metric-label">produtos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        cor = "alerta" if len(vencimento) > 0 else "metric-card"
        st.markdown(f"""
        <div class="{cor}">
            <div class="metric-label">Vencem em 30 dias</div>
            <div class="metric-value">{len(vencimento)}</div>
            <div class="metric-label">produtos</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Valor do estoque</div>
            <div class="metric-value">R$ {valor_total_estoque:,.2f}</div>
            <div class="metric-label">capital imobilizado</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabelas de ação
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.markdown("### ⚠️ Produtos para repor")
        if reposicao:
            df = pd.DataFrame(reposicao)[["descricao", "localizacao", "quantidade_atual", "estoque_minimo", "quantidade_faltante"]]
            df.columns = ["Produto", "Local", "Atual", "Mínimo", "Faltando"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("Nenhum produto abaixo do mínimo.")

    with col_dir:
        st.markdown("### ⏰ Vencem em 30 dias")
        if vencimento:
            df = pd.DataFrame(vencimento)[["descricao", "localizacao", "quantidade", "validade", "dias_para_vencer"]]
            df.columns = ["Produto", "Local", "Qtd", "Validade", "Dias"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("Nenhum produto vencendo em breve.")