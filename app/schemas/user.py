"""
Schemas de Usuario.

Define os schemas Pydantic para validacao de entrada e serializacao
de saida nos endpoints de usuario. Cada schema tem uma responsabilidade:

- UserCreate      -> Dados necessarios para criar um usuario.
- UserUpdate      -> Dados opcionais para atualizacao parcial.
- UserResponse    -> Representacao completa retornada pela API.
- UserListResponse -> Lista paginada de usuarios.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Campos compartilhados entre criacao e resposta."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome completo do usuario",
        examples=["Joao Silva"],
    )
    email: EmailStr = Field(
        ...,
        description="E-mail do usuario",
        examples=["joao@email.com"],
    )


class UserCreate(UserBase):
    """Schema para criacao de um novo usuario."""

    pass


class UserUpdate(BaseModel):
    """
    Schema para atualizacao parcial de usuario.

    Todos os campos sao opcionais. Apenas os campos
    enviados na requisicao serao atualizados.
    """

    name: str | None = Field(
        None,
        min_length=2,
        max_length=255,
        description="Nome completo do usuario",
    )
    email: EmailStr | None = Field(
        None,
        description="E-mail do usuario",
    )
    is_active: bool | None = Field(
        None,
        description="Status ativo do usuario",
    )


class UserResponse(UserBase):
    """Schema de resposta contendo todos os dados do usuario."""

    id: int = Field(..., description="ID unico do usuario")
    is_active: bool = Field(..., description="Status ativo do usuario")
    created_at: datetime = Field(..., description="Data de criacao")
    updated_at: datetime = Field(..., description="Data da ultima atualizacao")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema de resposta para listagem paginada de usuarios."""

    users: list[UserResponse] = Field(..., description="Lista de usuarios")
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., description="Pagina atual")
    per_page: int = Field(..., description="Itens por pagina")
