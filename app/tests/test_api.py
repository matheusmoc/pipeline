"""
Testes da API.

Suite de testes cobrindo todos os endpoints da aplicacao.
Utiliza pytest com TestClient do FastAPI e um banco SQLite
em memoria para isolar cada teste.

Cobertura:
    - Health Check e Info
    - CRUD completo de usuarios (criacao, leitura, atualizacao, remocao)
    - Validacoes de entrada (email invalido, nome curto, duplicidade)
    - Paginacao
    - Rotas inexistentes e metodos nao permitidos
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Banco de dados em memoria exclusivo para testes.
# StaticPool garante que a mesma conexao seja reutilizada
# durante toda a sessao de testes.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Substitui a sessao real pela sessao de testes."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Cria as tabelas antes de cada teste e remove depois."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Retorna uma instancia do TestClient."""
    return TestClient(app)


class TestHealthCheck:
    """Testes para o endpoint de health check."""

    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_has_message(self, client):
        response = client.get("/health")
        data = response.json()
        assert "message" in data


class TestAppInfo:
    """Testes para o endpoint de informacoes da aplicacao."""

    def test_info_returns_200(self, client):
        response = client.get("/info")
        assert response.status_code == 200

    def test_info_contains_app_name(self, client):
        response = client.get("/info")
        data = response.json()
        assert "app_name" in data

    def test_info_contains_version(self, client):
        response = client.get("/info")
        data = response.json()
        assert "version" in data


class TestCreateUser:
    """Testes para criacao de usuarios."""

    def test_create_user_success(self, client):
        response = client.post(
            "/api/v1/users",
            json={"name": "Joao Silva", "email": "joao@email.com"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Joao Silva"
        assert data["email"] == "joao@email.com"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_user_duplicate_email(self, client):
        user_data = {"name": "Joao Silva", "email": "joao@email.com"}
        client.post("/api/v1/users", json=user_data)

        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 409

    def test_create_user_invalid_email(self, client):
        response = client.post(
            "/api/v1/users",
            json={"name": "Joao Silva", "email": "email-invalido"},
        )
        assert response.status_code == 422

    def test_create_user_missing_name(self, client):
        response = client.post(
            "/api/v1/users",
            json={"email": "joao@email.com"},
        )
        assert response.status_code == 422

    def test_create_user_name_too_short(self, client):
        response = client.post(
            "/api/v1/users",
            json={"name": "J", "email": "joao@email.com"},
        )
        assert response.status_code == 422


class TestListUsers:
    """Testes para listagem de usuarios."""

    def test_list_users_empty(self, client):
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert data["users"] == []
        assert data["total"] == 0

    def test_list_users_with_data(self, client):
        client.post("/api/v1/users", json={"name": "User 1", "email": "user1@test.com"})
        client.post("/api/v1/users", json={"name": "User 2", "email": "user2@test.com"})

        response = client.get("/api/v1/users")
        data = response.json()
        assert data["total"] == 2
        assert len(data["users"]) == 2

    def test_list_users_pagination(self, client):
        for i in range(5):
            client.post("/api/v1/users", json={"name": f"User {i}", "email": f"user{i}@test.com"})

        response = client.get("/api/v1/users?page=1&per_page=2")
        data = response.json()
        assert len(data["users"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2


class TestGetUser:
    """Testes para busca de usuario por ID."""

    def test_get_user_success(self, client):
        create_response = client.post(
            "/api/v1/users",
            json={"name": "Joao Silva", "email": "joao@email.com"},
        )
        user_id = create_response.json()["id"]

        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Joao Silva"

    def test_get_user_not_found(self, client):
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404


class TestUpdateUser:
    """Testes para atualizacao de usuarios."""

    def test_update_user_success(self, client):
        create_response = client.post(
            "/api/v1/users",
            json={"name": "Joao Silva", "email": "joao@email.com"},
        )
        user_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"name": "Joao Santos"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Joao Santos"

    def test_update_user_not_found(self, client):
        response = client.put(
            "/api/v1/users/99999",
            json={"name": "Nome Novo"},
        )
        assert response.status_code == 404

    def test_update_user_duplicate_email(self, client):
        client.post("/api/v1/users", json={"name": "User 1", "email": "user1@test.com"})
        create_response = client.post(
            "/api/v1/users",
            json={"name": "User 2", "email": "user2@test.com"},
        )
        user_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"email": "user1@test.com"},
        )
        assert response.status_code == 409


class TestDeleteUser:
    """Testes para remocao de usuarios."""

    def test_delete_user_success(self, client):
        create_response = client.post(
            "/api/v1/users",
            json={"name": "Joao Silva", "email": "joao@email.com"},
        )
        user_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 200

        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        response = client.delete("/api/v1/users/99999")
        assert response.status_code == 404


class TestInvalidRoutes:
    """Testes para rotas invalidas e tratamento de erros."""

    def test_invalid_route_returns_404(self, client):
        response = client.get("/rota-inexistente")
        assert response.status_code == 404

    def test_invalid_method(self, client):
        response = client.patch("/health")
        assert response.status_code == 405

    def test_metrics_endpoint_exists(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
