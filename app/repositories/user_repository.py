"""
Repositorio de Usuarios.

Implementa o padrao Repository para isolar toda a logica de acesso
a dados do restante da aplicacao. Nenhuma regra de negocio deve
existir aqui; esse modulo apenas executa operacoes CRUD no banco.

Caso o banco de dados seja trocado no futuro, apenas este modulo
(e o database.py) precisam ser alterados.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository:
    """
    Repositorio responsavel pelas operacoes de persistencia
    da entidade User.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Retorna uma lista paginada de usuarios."""
        logger.debug(f"Buscando usuarios: skip={skip}, limit={limit}")
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_by_id(self, user_id: int) -> User | None:
        """Busca um usuario pelo ID. Retorna None se nao encontrado."""
        logger.debug(f"Buscando usuario por ID: {user_id}")
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        """Busca um usuario pelo e-mail. Retorna None se nao encontrado."""
        logger.debug(f"Buscando usuario por e-mail: {email}")
        return self.db.query(User).filter(User.email == email).first()

    def count(self) -> int:
        """Retorna o total de usuarios cadastrados."""
        return self.db.query(User).count()

    def create(self, user_data: UserCreate) -> User:
        """
        Insere um novo usuario no banco de dados.

        Recebe os dados ja validados pelo schema, cria a instancia
        do modelo, persiste e retorna o objeto com o ID gerado.
        """
        logger.info(f"Criando novo usuario: {user_data.email}")
        db_user = User(
            name=user_data.name,
            email=user_data.email,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Usuario criado com sucesso: ID={db_user.id}")
        return db_user

    def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        """
        Atualiza os campos de um usuario existente.

        Apenas os campos enviados na requisicao (exclude_unset)
        sao alterados, preservando os demais valores.
        Retorna None caso o usuario nao exista.
        """
        logger.info(f"Atualizando usuario: ID={user_id}")
        db_user = self.get_by_id(user_id)
        if not db_user:
            logger.warning(f"Usuario nao encontrado para atualizacao: ID={user_id}")
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Usuario atualizado com sucesso: ID={user_id}")
        return db_user

    def delete(self, user_id: int) -> bool:
        """
        Remove um usuario do banco de dados.

        Retorna True se a remocao foi bem-sucedida,
        False caso o usuario nao exista.
        """
        logger.info(f"Removendo usuario: ID={user_id}")
        db_user = self.get_by_id(user_id)
        if not db_user:
            logger.warning(f"Usuario nao encontrado para remocao: ID={user_id}")
            return False

        self.db.delete(db_user)
        self.db.commit()
        logger.info(f"Usuario removido com sucesso: ID={user_id}")
        return True
