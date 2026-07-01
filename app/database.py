"""
Configuracao do banco de dados.

Configura o SQLAlchemy com engine, session factory e base declarativa.
Utiliza SQLite por padrao para simplificar o setup inicial, mas a
troca para PostgreSQL ou MySQL e feita apenas alterando a variavel
DATABASE_URL no .env, sem necessidade de modificar este modulo.

A funcao get_db() e usada como Dependency Injection nos endpoints
para fornecer uma sessao de banco que e automaticamente fechada
apos o termino da requisicao.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""

    pass


def create_tables():
    """Cria todas as tabelas definidas nos modelos, caso ainda nao existam."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Fornece uma sessao do banco de dados via Dependency Injection.

    Abre a sessao no inicio da requisicao e garante o fechamento
    ao final, mesmo em caso de excecao.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
