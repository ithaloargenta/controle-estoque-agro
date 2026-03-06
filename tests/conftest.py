import os
import pytest
import bcrypt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from app.infrastructure.database.connection import get_db
from main import app

TEST_DATABASE_URL = "postgresql://estoque_user:estoque_pass@db:5432/estoque_test"

engine_test = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def resetar_banco():
    with engine_test.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    os.environ["TEST_DATABASE_URL"] = TEST_DATABASE_URL
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    del os.environ["TEST_DATABASE_URL"]


@pytest.fixture(scope="session", autouse=True)
def criar_banco_teste():
    resetar_banco()
    yield


@pytest.fixture(autouse=True)
def limpar_banco():
    db = TestingSessionLocal()
    try:
        db.execute(text("""
            TRUNCATE TABLE movimentacao, estoque, produto_fornecedor,
            nfe_importada, produto, fornecedor, usuario RESTART IDENTITY CASCADE
        """))
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def token(client):
    from app.infrastructure.models.usuario import UsuarioModel

    senha_hash = bcrypt.hashpw("senha123".encode(), bcrypt.gensalt()).decode()

    db = TestingSessionLocal()
    usuario = UsuarioModel(
        email="teste@teste.com",
        nome="Usuário Teste",
        senha_hash=senha_hash,
        ativo=True,
    )
    db.add(usuario)
    db.commit()
    db.close()

    response = client.post("/auth/login", data={
        "username": "teste@teste.com",
        "password": "senha123",
    })
    return response.json()["access_token"]


@pytest.fixture
def headers(token):
    return {"Authorization": f"Bearer {token}"}