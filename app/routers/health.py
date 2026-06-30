"""
Rota de Health Check.

Endpoint utilizado por load balancers, orquestradores (Kubernetes, Docker)
e ferramentas de monitoramento para verificar se a aplicacao esta
respondendo corretamente.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Verifica se a aplicacao esta em execucao e saudavel.",
)
def health_check():
    """Retorna o status de saude da aplicacao."""
    return {
        "status": "healthy",
        "message": "A aplicacao esta funcionando corretamente.",
    }
