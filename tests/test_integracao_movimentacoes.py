def test_entrada_manual(client, headers):
    resp = client.post("/produtos/", json={
        "descricao": "Produto Entrada Teste",
        "unidade_comercial": "UN",
    }, headers=headers)
    produto_id = resp.json()["id"]

    response = client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "ENTRADA",
        "quantidade": 10,
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "ENTRADA"
    assert float(data["quantidade"]) == 10.0


def test_saida_atualiza_estoque(client, headers):
    resp = client.post("/produtos/", json={
        "descricao": "Produto Saida Teste",
        "unidade_comercial": "UN",
    }, headers=headers)
    produto_id = resp.json()["id"]

    client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "ENTRADA",
        "quantidade": 10,
    }, headers=headers)

    response = client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "SAIDA",
        "quantidade": 3,
    }, headers=headers)

    print("RESPOSTA SAIDA:", response.json())
    assert response.status_code == 201

    estoque = client.get("/estoque/enriquecido", headers=headers).json()
    item = next((e for e in estoque if e["produto_id"] == produto_id), None)
    assert item is not None
    assert float(item["quantidade"]) == 7.0


def test_saida_saldo_insuficiente(client, headers):
    resp = client.post("/produtos/", json={
        "descricao": "Produto Sem Saldo",
        "unidade_comercial": "UN",
    }, headers=headers)
    produto_id = resp.json()["id"]

    response = client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "SAIDA",
        "quantidade": 5,
    }, headers=headers)

    assert response.status_code == 400


def test_entrada_produto_com_validade(client, headers):
    resp = client.post("/produtos/", json={
        "descricao": "Vacina Teste",
        "unidade_comercial": "UN",
        "requer_validade": True,
    }, headers=headers)
    produto_id = resp.json()["id"]

    response = client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "ENTRADA",
        "quantidade": 5,
    }, headers=headers)
    assert response.status_code == 400

    response = client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "ENTRADA",
        "quantidade": 5,
        "validade": "2027-01-01",
    }, headers=headers)
    assert response.status_code == 201


def test_ajuste_sem_motivo(client, headers):
    resp = client.post("/produtos/", json={
        "descricao": "Produto Ajuste Teste",
        "unidade_comercial": "UN",
    }, headers=headers)
    produto_id = resp.json()["id"]

    client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "ENTRADA",
        "quantidade": 10,
    }, headers=headers)

    response = client.post("/movimentacoes/", json={
        "produto_id": produto_id,
        "localizacao": "LOJA",
        "tipo": "AJUSTE_SAIDA",
        "quantidade": 3,
    }, headers=headers)
    assert response.status_code == 400