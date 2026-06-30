"""
Middleware de Logging.

Intercepta todas as requisicoes HTTP para registrar metodo, URL,
IP do cliente, status code e tempo de processamento. As informacoes
sao enviadas para stdout em formato estruturado, facilitando a
integracao com ferramentas como Dozzle e ELK Stack.

O header X-Process-Time e adicionado automaticamente em cada
resposta para facilitar debugging de performance.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware que registra detalhes de cada requisicao e resposta."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Processa a requisicao registrando entrada, saida e tempo gasto.

        Fluxo:
            1. Registra a requisicao de entrada (metodo, path, IP).
            2. Encaminha para o proximo handler na cadeia.
            3. Calcula o tempo total de processamento.
            4. Registra a resposta (status, tempo).
            5. Adiciona o header X-Process-Time.
        """
        start_time = time.time()

        logger.info(
            f"Requisicao recebida: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"Resposta enviada: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Tempo: {process_time:.4f}s",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            },
        )

        response.headers["X-Process-Time"] = str(round(process_time, 4))

        return response
