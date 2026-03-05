import streamlit as st
from services.api import login


def fazer_login(email: str, senha: str) -> bool:
    resultado = login(email, senha)
    if resultado:
        st.session_state["token"] = resultado["access_token"]
        st.session_state["autenticado"] = True
        return True
    return False


def fazer_logout():
    st.session_state.clear()


def esta_autenticado() -> bool:
    return st.session_state.get("autenticado", False)