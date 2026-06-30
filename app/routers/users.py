"""
Rotas de Usuarios.

Define os endpoints REST para operacoes CRUD de usuarios.
Cada endpoint recebe o servico via Dependency Injection, garantindo
que a logica de negocio fique isolada na camada de servico.

Endpoints disponiveis:
    GET    /api/v1/users          -> Listagem paginada
    GET    /api/v1/users/{id}     -> Busca por ID
    POST   /api/v1/users          -> Criacao
    PUT    /api/v1/users/{id}     -> Atualizacao
    DELETE /api/v1/users/{id}     -> Remocao
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Injeta a sessao do banco no servico de usuarios."""
    return UserService(db)


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Retorna uma lista paginada de todos os usuarios cadastrados.",
)
def list_users(
    page: int = Query(1, ge=1, description="Pagina atual"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por pagina"),
    service: UserService = Depends(get_user_service),
):
    """Lista todos os usuarios com suporte a paginacao."""
    return service.list_users(page=page, per_page=per_page)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Buscar usuario",
    description="Retorna os dados de um usuario especifico pelo ID.",
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """Busca um usuario pelo ID."""
    return service.get_user(user_id)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuario",
    description="Cria um novo usuario com os dados fornecidos.",
)
def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """Cria um novo usuario."""
    return service.create_user(user_data)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Atualizar usuario",
    description="Atualiza os dados de um usuario existente.",
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    """Atualiza um usuario existente."""
    return service.update_user(user_id, user_data)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Remover usuario",
    description="Remove um usuario pelo ID.",
)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """Remove um usuario pelo ID."""
    return service.delete_user(user_id)
