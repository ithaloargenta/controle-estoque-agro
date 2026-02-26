from fastapi import FastAPI

import app.infrastructure.models.base  # noqa: F401 — registra todos os modelos SQLAlchemy
from app.api.routers.auth import router as auth_router
from app.api.routers.produtos import router as produtos_router
from app.api.routers.fornecedores import router as fornecedores_router
from app.api.routers.movimentacoes import router as movimentacoes_router
from app.api.routers.estoque import router as estoque_router
from app.api.routers.usuarios import router as usuarios_router
from app.api.routers.importacao import router as importacao_router

app = FastAPI(
    title="Sistema de Controle de Estoque",
    description="Sistema interno para controle de estoque agropecuário",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(produtos_router)
app.include_router(fornecedores_router)
app.include_router(movimentacoes_router)
app.include_router(estoque_router)
app.include_router(usuarios_router)
app.include_router(importacao_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}