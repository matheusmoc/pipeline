"""
Ponto de entrada principal da aplicacao FastAPI.

Responsavel por inicializar a aplicacao, registrar middlewares,
incluir rotas, configurar instrumentacao de metricas e definir
handlers globais de excecoes.

O ciclo de vida (lifespan) garante que as tabelas do banco
sejam criadas na inicializacao e que recursos sejam liberados
no encerramento.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables
from app.middleware.logging_middleware import LoggingMiddleware
from app.routers import health, info, users
from app.utils.logger import get_logger
from app.utils.metrics import setup_metrics

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicacao.

    Na inicializacao, cria as tabelas do banco de dados.
    No encerramento, registra o evento para fins de auditoria.
    """
    logger.info("Inicializando aplicacao...")
    create_tables()
    logger.info("Tabelas do banco de dados criadas/verificadas.")
    yield
    logger.info("Encerrando aplicacao...")


app = FastAPI(
    title=settings.APP_NAME,
    description="API REST para demonstracao de pipeline CI/CD moderno com FastAPI, Docker, GitHub Actions e observabilidade.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(LoggingMiddleware)

# Metricas Prometheus
setup_metrics(app)


app.include_router(health.router, tags=["Health"])
app.include_router(info.router, tags=["Info"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para excecoes nao tratadas.

    Captura qualquer excecao nao prevista pelos handlers especificos,
    registra o erro com detalhes da requisicao e retorna uma resposta
    padronizada ao cliente sem expor informacoes internas.
    """
    logger.error(
        f"Erro nao tratado: {exc}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "error": str(exc),
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor.",
            "type": "internal_server_error",
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Handler para rotas nao encontradas.

    Retorna uma resposta JSON padronizada quando o cliente
    tenta acessar um endpoint que nao existe na aplicacao.
    """
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Recurso nao encontrado.",
            "type": "not_found",
        },
    )
