"""
Modelo de Usuario.

Define a tabela 'users' no banco de dados utilizando SQLAlchemy.
Cada registro representa um usuario da aplicacao com informacoes
basicas de cadastro e controle de atividade.
"""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database import Base


class User(Base):
    """
    Representa um usuario no banco de dados.

    Campos:
        id         - Chave primaria auto-incrementada.
        name       - Nome completo do usuario.
        email      - E-mail unico utilizado como identificador.
        is_active  - Flag que indica se o usuario esta ativo no sistema.
        created_at - Timestamp de criacao do registro.
        updated_at - Timestamp da ultima atualizacao, preenchido automaticamente.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
