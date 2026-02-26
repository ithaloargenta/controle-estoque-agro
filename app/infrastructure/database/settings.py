from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # ignora variáveis do .env que não estão declaradas aqui
    }


settings = Settings()