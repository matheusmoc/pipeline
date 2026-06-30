"""
Configuracoes da aplicacao.

Centraliza todas as configuracoes utilizando Pydantic Settings.
Os valores sao carregados de variaveis de ambiente ou de um
arquivo .env na raiz do projeto, o que facilita a troca entre
ambientes (desenvolvimento, homologacao, producao) sem alterar codigo.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Classe de configuracoes carregadas automaticamente
    a partir de variaveis de ambiente.
    """

    # Aplicacao
    APP_NAME: str = "FastAPI Seminario CI/CD"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Banco de Dados
    DATABASE_URL: str = "sqlite:///./app.db"

    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
