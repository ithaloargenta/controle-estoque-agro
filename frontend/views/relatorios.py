import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from io import BytesIO
from services.api import get


def exportar_excel(df: pd.DataFrame, nome: str):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Relatório")
    st.download_button(
        label="📥 Exportar Excel",
        data=buffer.getvalue(),
        file_name=f"{nome}_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def render():
    st.title("📊 Relatórios")

    aba = st.tabs([
        "Reposição",
        "Vencimento",
        "Vencidos",
        "Giro",
        "Gasto por fornecedor",
        "Valor do estoque",
        "Sem movimentação",
        "Curva ABC",
        "Preço de custo",
        "Sazonalidade",
        "Comparativo mensal",
    ])

    # --- R01 Reposição ---
    with aba[0]:
        st.markdown("### Lista de reposição")
        dados = get("/relatorios/reposicao") or []
        if not dados:
            st.success("Nenhum produto abaixo do mínimo.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["descricao", "localizacao", "quantidade_atual", "estoque_minimo", "quantidade_faltante"]].copy()
            df_exibir.columns = ["Produto", "Local", "Atual", "Mínimo", "Faltando"]
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "reposicao")

            fig = px.bar(
                df_exibir, x="Produto", y="Faltando",
                title="Quantidade faltando por produto",
                color="Faltando", color_continuous_scale="Reds",
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    # --- R02 Vencimento ---
    with aba[1]:
        st.markdown("### Produtos próximos ao vencimento")
        dias = st.number_input("Dias para vencimento", min_value=1, value=30, step=1)
        dados = get("/relatorios/vencimento", params={"dias": dias}) or []
        if not dados:
            st.success(f"Nenhum produto vencendo nos próximos {dias} dias.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["descricao", "localizacao", "quantidade", "validade", "dias_para_vencer"]].copy()
            df_exibir.columns = ["Produto", "Local", "Quantidade", "Validade", "Dias restantes"]
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "vencimento")

    # --- R03 Vencidos ---
    with aba[2]:
        st.markdown("### Produtos vencidos")
        dados = get("/relatorios/vencidos") or []
        if not dados:
            st.success("Nenhum produto vencido em estoque.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["descricao", "localizacao", "quantidade", "validade", "dias_vencido"]].copy()
            df_exibir.columns = ["Produto", "Local", "Quantidade", "Validade", "Dias vencido"]
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "vencidos")

    # --- R04 Giro ---
    with aba[3]:
        st.markdown("### Giro por produto no período")
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data início", value=date(date.today().year, date.today().month, 1), key="giro_inicio")
        with col2:
            data_fim = st.date_input("Data fim", value=date.today(), key="giro_fim")

        dados = get("/relatorios/giro", params={
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
        }) or []

        if not dados:
            st.info("Nenhuma saída no período.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["descricao", "unidade_comercial", "quantidade_saida", "quantidade_saida_periodo_anterior", "variacao_percentual"]].copy()
            df_exibir.columns = ["Produto", "Unidade", "Saídas", "Período anterior", "Variação %"]
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "giro")

            fig = px.bar(
                df_exibir, x="Produto", y="Saídas",
                title="Volume de saídas por produto",
                color="Saídas", color_continuous_scale="Blues",
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    # --- R05 Gasto por fornecedor ---
    with aba[4]:
        st.markdown("### Gasto por fornecedor")
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data início", value=date(date.today().year, date.today().month, 1), key="forn_inicio")
        with col2:
            data_fim = st.date_input("Data fim", value=date.today(), key="forn_fim")

        dados = get("/relatorios/gasto-fornecedor", params={
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
        }) or []

        if not dados:
            st.info("Nenhuma entrada com valor no período.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["razao_social", "total_entradas", "valor_total"]].copy()
            df_exibir.columns = ["Fornecedor", "Entradas", "Valor total (R$)"]
            df_exibir["Valor total (R$)"] = df_exibir["Valor total (R$)"].apply(lambda x: f"R$ {float(x):,.2f}")
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "gasto_fornecedor")

            fig = px.pie(
                df, values=df["valor_total"].astype(float),
                names="razao_social",
                title="Distribuição de gastos por fornecedor",
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- R08 Valor do estoque ---
    with aba[5]:
        st.markdown("### Valor total do estoque")
        dados = get("/relatorios/valor-estoque")
        if not dados or not dados.get("itens"):
            st.info("Nenhum produto em estoque com preço de custo.")
        else:
            total = float(dados["valor_total_geral"])
            st.metric("💰 Capital imobilizado", f"R$ {total:,.2f}")

            df = pd.DataFrame(dados["itens"])
            df_exibir = df[["descricao", "localizacao", "quantidade", "ultimo_preco_custo", "valor_total"]].copy()
            df_exibir.columns = ["Produto", "Local", "Quantidade", "Último custo", "Valor total"]
            df_exibir["Último custo"] = df_exibir["Último custo"].apply(lambda x: f"R$ {float(x):,.2f}" if x else "-")
            df_exibir["Valor total"] = df_exibir["Valor total"].apply(lambda x: f"R$ {float(x):,.2f}" if x else "-")
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "valor_estoque")

            fig = px.bar(
                df, x="descricao", y=df["valor_total"].astype(float),
                title="Valor em estoque por produto",
                orientation="v",
                color=df["valor_total"].astype(float),
                color_continuous_scale="Blues",
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    # --- R07 Sem movimentação ---
    with aba[6]:
        st.markdown("### Produtos sem movimentação")
        dias = st.slider("Produtos parados há mais de X dias", 30, 365, 90)
        dados = get("/relatorios/sem-movimentacao", params={"dias": dias}) or []
        if not dados:
            st.success(f"Todos os produtos tiveram movimentação nos últimos {dias} dias.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["descricao", "unidade_comercial", "quantidade_atual", "ultima_movimentacao", "dias_parado"]].copy()
            df_exibir.columns = ["Produto", "Unidade", "Quantidade", "Última movimentação", "Dias parado"]
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "sem_movimentacao")

    # --- R09 Curva ABC ---
    with aba[7]:
        st.markdown("### Curva ABC por categoria NCM")
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data início", value=date(date.today().year, 1, 1), key="abc_inicio")
        with col2:
            data_fim = st.date_input("Data fim", value=date.today(), key="abc_fim")

        dados = get("/relatorios/curva-abc", params={
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
        }) or []

        if not dados:
            st.info("Nenhuma saída no período.")
        else:
            df = pd.DataFrame(dados)
            df_exibir = df[["ncm_prefixo", "descricao_ncm", "quantidade_total_saida", "percentual", "percentual_acumulado", "classificacao"]].copy()
            df_exibir.columns = ["NCM", "Categoria", "Saídas", "% do total", "% acumulado", "Classe"]
            st.dataframe(df_exibir, use_container_width=True, hide_index=True)
            exportar_excel(df_exibir, "curva_abc")

            fig = px.pie(
                df, values=df["quantidade_total_saida"].astype(float),
                names="descricao_ncm",
                title="Distribuição de saídas por categoria NCM",
                color="classificacao",
                color_discrete_map={"A": "#1e3a5f", "B": "#2e7bc4", "C": "#a8c8e8"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- R10 Preço de custo ---
    with aba[8]:
        st.markdown("### Evolução de preço de custo")
        estoque = get("/estoque/enriquecido") or []
        produtos_map = {item["descricao"]: item["produto_id"] for item in estoque}

        if not produtos_map:
            st.info("Nenhum produto cadastrado.")
        else:
            produto_nome = st.selectbox("Produto", options=list(produtos_map.keys()), key="preco_produto")
            produto_id = produtos_map[produto_nome]
            dados = get(f"/relatorios/preco-custo/{produto_id}")

            if dados and dados.get("historico"):
                df = pd.DataFrame(dados["historico"])
                df_exibir = df[["criado_em", "valor_unitario", "quantidade", "variacao_percentual"]].copy()
                df_exibir.columns = ["Data", "Valor unitário", "Quantidade", "Variação %"]
                df_exibir["Valor unitário"] = df_exibir["Valor unitário"].apply(lambda x: f"R$ {float(x):,.2f}")
                st.dataframe(df_exibir, use_container_width=True, hide_index=True)
                exportar_excel(df_exibir, "preco_custo")

                df["valor_unitario"] = df["valor_unitario"].astype(float)
                df["criado_em"] = pd.to_datetime(df["criado_em"])
                fig = px.line(
                    df, x="criado_em", y="valor_unitario",
                    title=f"Evolução do preço de custo — {produto_nome}",
                    markers=True,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhuma entrada com valor registrada para este produto.")

    # --- R11 Sazonalidade ---
    with aba[9]:
        st.markdown("### Sazonalidade por categoria")
        ano = st.number_input("Ano", min_value=2020, max_value=2030, value=date.today().year)
        dados = get("/relatorios/sazonalidade", params={"ano": ano}) or []

        if not dados:
            st.info("Nenhuma saída registrada no ano.")
        else:
            df = pd.DataFrame(dados)
            meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                     "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

            linhas = []
            for _, row in df.iterrows():
                for mes in meses:
                    linhas.append({
                        "Categoria": row["descricao_ncm"],
                        "Mês": mes.capitalize(),
                        "Quantidade": float(row["dados_mensais"].get(mes, 0)),
                    })

            df_long = pd.DataFrame(linhas)
            fig = px.line(
                df_long, x="Mês", y="Quantidade", color="Categoria",
                title=f"Sazonalidade por categoria — {ano}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
            exportar_excel(df_long, "sazonalidade")

    # --- R12 Comparativo mensal ---
    with aba[10]:
        st.markdown("### Comparativo mensal")
        col1, col2 = st.columns(2)
        with col1:
            mes1 = st.text_input("Mês 1 (AAAA-MM)", value=f"{date.today().year}-{date.today().month-1:02d}", key="comp_mes1")
        with col2:
            mes2 = st.text_input("Mês 2 (AAAA-MM)", value=f"{date.today().year}-{date.today().month:02d}", key="comp_mes2")

        dados = get("/relatorios/comparativo-mensal", params={
            "ano_mes_1": mes1,
            "ano_mes_2": mes2,
        }) or []

        if not dados:
            st.info("Nenhuma movimentação nos períodos selecionados.")
        else:
            # Totais do mês
            total_valor_mes1 = sum(float(d["mes_1"]["valor_entradas"]) for d in dados)
            total_valor_mes2 = sum(float(d["mes_2"]["valor_entradas"]) for d in dados)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"💰 Total entradas {mes1}", f"R$ {total_valor_mes1:,.2f}")
            with col2:
                st.metric(f"💰 Total entradas {mes2}", f"R$ {total_valor_mes2:,.2f}")

            st.markdown("---")

            df = pd.DataFrame([{
                "Produto": d["descricao"],
                f"Entradas {mes1}": float(d["mes_1"]["entradas"]),
                f"Entradas {mes2}": float(d["mes_2"]["entradas"]),
                f"Saídas {mes1}": float(d["mes_1"]["saidas"]),
                f"Saídas {mes2}": float(d["mes_2"]["saidas"]),
                f"Valor entradas {mes1}": f"R$ {float(d['mes_1']['valor_entradas']):,.2f}",
                f"Valor entradas {mes2}": f"R$ {float(d['mes_2']['valor_entradas']):,.2f}",
                "Var. entradas %": d["variacao_entradas"],
                "Var. saídas %": d["variacao_saidas"],
            } for d in dados])

            st.dataframe(df, use_container_width=True, hide_index=True)
            exportar_excel(df, "comparativo_mensal")

            fig = px.bar(
                df, x="Produto",
                y=[f"Entradas {mes1}", f"Entradas {mes2}"],
                barmode="group",
                title="Comparativo de entradas",
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)