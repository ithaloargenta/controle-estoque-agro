import pytest


def test_cadastrar_produto(client, headers):
    response = client.post("/produtos/", json={
        "descricao": "Produto Integração Teste",
        "unidade_comercial": "UN",
        "ncm": "30021590",
        "requer_validade": False,
        "estoque_minimo": 5,
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["descricao"] == "Produto Integração Teste"
    assert data["unidade_comercial"] == "UN"
    assert data["ativo"] is True


def test_listar_produtos(client, headers):
    # Cadastra dois produtos
    client.post("/produtos/", json={
        "descricao": "Produto A",
        "unidade_comercial": "UN",
    }, headers=headers)
    client.post("/produtos/", json={
        "descricao": "Produto B",
        "unidade_comercial": "KG",
    }, headers=headers)

    response = client.get("/produtos/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_desativar_produto(client, headers):
    # Cadastra produto
    resp = client.post("/produtos/", json={
        "descricao": "Produto Para Desativar",
        "unidade_comercial": "UN",
    }, headers=headers)
    produto_id = resp.json()["id"]

    # Desativa
    response = client.patch(f"/produtos/{produto_id}/desativar", headers=headers)
    assert response.status_code == 200

    # Verifica que não aparece mais na listagem
    lista = client.get("/produtos/", headers=headers).json()
    ids = [p["id"] for p in lista]
    assert produto_id not in ids


def test_cadastrar_produto_sem_descricao(client, headers):
    response = client.post("/produtos/", json={
        "unidade_comercial": "UN",
    }, headers=headers)
    assert response.status_code == 422