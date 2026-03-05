import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


def get_headers() -> dict:
    token = st.session_state.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def login(email: str, senha: str) -> dict | None:
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": email, "password": senha},
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def get(endpoint: str, params: dict = None) -> dict | list | None:
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            headers=get_headers(),
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def post(endpoint: str, data: dict = None, files: dict = None, params: dict = None) -> dict | None:
    try:
        if files:
            response = requests.post(
                f"{API_URL}{endpoint}",
                headers=get_headers(),
                files=files,
                params=params,
            )
        else:
            response = requests.post(
                f"{API_URL}{endpoint}",
                headers=get_headers(),
                json=data,
                params=params,
            )
        if response.status_code in (200, 201):
            return response.json()
        st.error(f"Erro: {response.json().get('detail', 'Erro desconhecido')}")
        return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None


def put(endpoint: str, data: dict = None) -> dict | None:
    try:
        response = requests.put(
            f"{API_URL}{endpoint}",
            headers=get_headers(),
            json=data,
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"Erro: {response.json().get('detail', 'Erro desconhecido')}")
        return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None