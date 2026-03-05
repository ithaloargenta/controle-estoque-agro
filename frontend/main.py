import streamlit as st
from services.auth import esta_autenticado, fazer_login, fazer_logout

st.set_page_config(
    page_title="Estoque Agropecuário",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1565C0;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        padding: 6px 0 !important;
    }
    [data-testid="stSidebar"] .stRadio div {
        gap: 4px;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2);
    }
    [data-testid="stSidebar"] button {
        background-color: rgba(255,255,255,0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255,255,255,0.25) !important;
    }

    /* Cabeçalho das páginas */
    h1 {
        color: #1565C0 !important;
        font-weight: 700 !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E3F2FD;
        margin-bottom: 1.5rem !important;
    }
    h2, h3 {
        color: #1A1A2E !important;
        font-weight: 600 !important;
    }

    /* Cartões do dashboard */
    .card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px 24px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #1565C0;
        margin-bottom: 12px;
    }
    .card-value {
        font-size: 32px;
        font-weight: 700;
        color: #1565C0;
        line-height: 1.2;
    }
    .card-label {
        font-size: 13px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .card-sub {
        font-size: 13px;
        color: #999;
        margin-top: 2px;
    }
    .card-warning {
        border-left-color: #F57C00;
    }
    .card-warning .card-value {
        color: #F57C00;
    }
    .card-danger {
        border-left-color: #C62828;
    }
    .card-danger .card-value {
        color: #C62828;
    }
    .card-success {
        border-left-color: #2E7D32;
    }
    .card-success .card-value {
        color: #2E7D32;
    }

    /* Botões primários */
    .stButton > button[kind="primary"] {
        background-color: #1565C0 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0D47A1 !important;
    }

    /* Tabelas */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 6px !important;
    }

    /* Remover padding excessivo */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Login */
    .login-container {
        background: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom: 2rem;">
            <span style="font-size: 48px;">🌾</span>
            <h2 style="color: #1565C0 !important; margin-top: 0.5rem;">Sistema de Estoque</h2>
            <p style="color: #666;">Acesse sua conta para continuar</p>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Entrar", use_container_width=True, type="primary"):
            if not email or not senha:
                st.error("Preencha email e senha.")
            elif fazer_login(email, senha):
                st.rerun()
            else:
                st.error("Email ou senha incorretos.")


def menu_lateral():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
            <span style="font-size: 36px;">🌾</span>
            <div style="font-size: 18px; font-weight: 700; color: white; margin-top: 8px;">Estoque</div>
            <div style="font-size: 12px; color: rgba(255,255,255,0.6);">Sistema Agropecuário</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        pagina = st.radio(
            "Navegação",
            options=[
                "🏠  Início",
                "📦  Estoque",
                "📋  Histórico",
                "📥  Importar NF-e",
                "➕  Entrada manual",
                "🔻  Saída",
                "🔧  Ajuste",
                "🛒  Produtos",
                "🏭  Fornecedores",
                "📊  Relatórios",
                "⚙️  Configurações",
            ],
            label_visibility="collapsed",
        )

        st.divider()
        if st.button("Sair", use_container_width=True):
            fazer_logout()
            st.rerun()

    return pagina


if not esta_autenticado():
    tela_login()
    st.stop()

pagina = menu_lateral()

if pagina == "🏠  Início":
    from views.inicio import render
    render()
elif pagina == "📦  Estoque":
    from views.estoque import render
    render()
elif pagina == "📋  Histórico":
    from views.historico import render
    render()
elif pagina == "📥  Importar NF-e":
    from views.importar_nfe import render
    render()
elif pagina == "➕  Entrada manual":
    from views.entrada_manual import render
    render()
elif pagina == "🔻  Saída":
    from views.saida import render
    render()
elif pagina == "🔧  Ajuste":
    from views.ajuste import render
    render()
elif pagina == "🛒  Produtos":
    from views.produtos import render
    render()
elif pagina == "🏭  Fornecedores":
    from views.fornecedores import render
    render()
elif pagina == "📊  Relatórios":
    from views.relatorios import render
    render()
elif pagina == "⚙️  Configurações":
    from views.configuracoes import render
    render()