"""
Rota de Informacoes da Aplicacao.

Retorna metadados como versao, ambiente, plataforma e timestamp.
Util para verificar rapidamente qual versao esta em producao
e em qual ambiente a instancia esta rodando.
"""

import platform
from datetime import UTC, datetime

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get(
    "/info",
    summary="Informacoes da Aplicacao",
    description="Retorna metadados e informacoes sobre a aplicacao.",
)
def app_info():
    """Retorna informacoes da aplicacao incluindo versao e ambiente."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "timestamp": datetime.now(UTC).isoformat(),
        "debug": settings.DEBUG,
    }
