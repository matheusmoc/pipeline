"""
Servico de Usuarios.

Implementa a camada de servico (Service Layer) que concentra as
regras de negocio relacionadas a usuarios. Este modulo orquestra
chamadas ao repositorio e realiza validacoes como unicidade de
e-mail e existencia do registro antes de operar.

Os endpoints nunca acessam o repositorio diretamente; sempre
passam pelo servico, mantendo a separacao de responsabilidades.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Servico responsavel pelas regras de negocio de usuarios."""

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def list_users(self, page: int = 1, per_page: int = 10) -> dict:
        """
        Lista usuarios com paginacao.

        Calcula o offset com base na pagina solicitada e retorna
        os registros junto com metadados de paginacao.
        """
        skip = (page - 1) * per_page
        users = self.repository.get_all(skip=skip, limit=per_page)
        total = self.repository.count()

        logger.info(f"Listando usuarios: page={page}, per_page={per_page}, total={total}")

        return {
            "users": users,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def get_user(self, user_id: int) -> User:
        """
        Busca um usuario pelo ID.

        Levanta HTTPException 404 caso o usuario nao exista.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"Usuario nao encontrado: ID={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario com ID {user_id} nao encontrado.",
            )
        return user

    def create_user(self, user_data: UserCreate) -> User:
        """
        Cria um novo usuario.

        Antes de inserir, verifica se o e-mail ja esta em uso.
        Caso positivo, retorna HTTPException 409 (Conflict).
        """
        existing_user = self.repository.get_by_email(user_data.email)
        if existing_user:
            logger.warning(f"E-mail ja em uso: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"E-mail '{user_data.email}' ja esta em uso.",
            )

        return self.repository.create(user_data)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Atualiza um usuario existente.

        Verifica se o usuario existe e, caso o e-mail esteja sendo
        alterado, valida se o novo e-mail nao pertence a outro usuario.
        """
        self.get_user(user_id)

        if user_data.email:
            existing = self.repository.get_by_email(user_data.email)
            if existing and existing.id != user_id:
                logger.warning(f"E-mail ja em uso por outro usuario: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"E-mail '{user_data.email}' ja esta em uso.",
                )

        updated_user = self.repository.update(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario com ID {user_id} nao encontrado.",
            )

        return updated_user

    def delete_user(self, user_id: int) -> dict:
        """
        Remove um usuario pelo ID.

        Confirma a existencia antes de tentar remover.
        Retorna mensagem de confirmacao em caso de sucesso.
        """
        self.get_user(user_id)

        success = self.repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao remover o usuario.",
            )

        logger.info(f"Usuario removido: ID={user_id}")
        return {"message": f"Usuario com ID {user_id} removido com sucesso."}
