from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.infrastructure.database.settings import settings


#Motor de conexão com o banco
#pool_pre_ping=True -> Verifica se a conexão ainda é válida antes de usá-la
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


#Fabrica de sessões para interagir com o banco de dados
#autocommit=False -> As transações precisam ser confirmadas explicitamente
#autoflush=False -> As alterações não são enviadas ao banco automaticamente, permitindo controle manual
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


#Classe base para todos os modelos SQLAlchemy
#Toda tabela que criamos vai herdar dessa classe, garantindo que todas tenham as funcionalidades básicas do SQLAlchemy
class Base(DeclarativeBase):
    pass


#Gerador de sessão para injeção de dependencias no FastAPI
#Garante que a sessão é sempre fechada ao final da requisição,
#mesmo que ocorra um erro durante o processamento
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()