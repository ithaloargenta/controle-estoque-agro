from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.infrastructure.database.settings import settings


def criar_token(data: dict) -> str:
    """Gera um JWT com os dados fornecidos e prazo de expiração."""
    payload = data.copy()
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expiracao})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verificar_token(token: str) -> dict:
    """Valida o token e retorna o payload. Lança JWTError se inválido."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Verifica se a senha em texto puro bate com o hash armazenado."""
    return bcrypt.checkpw(
        senha_plain.encode("utf-8"),
        senha_hash.encode("utf-8"),
    )