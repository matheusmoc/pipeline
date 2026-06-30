# Comandos utilitarios para desenvolvimento,
# testes, qualidade de codigo e operacoes Docker.

.PHONY: help install run test lint format docker-build docker-up docker-down docker-logs clean

PYTHON = python3
PIP = pip
DOCKER_COMPOSE = docker compose
APP_MODULE = app.main:app

help: ## Exibe esta mensagem de ajuda
	@echo "FastAPI Seminario CI/CD - Makefile"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""

# Desenvolvimento
install: ## Instala dependencias Python
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: ## Executa a aplicacao localmente com hot reload
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port 8000 --reload

test: ## Executa testes com pytest
	pytest app/tests/ -v --tb=short

test-cov: ## Executa testes com cobertura
	pytest app/tests/ -v --tb=short --cov=app --cov-report=html

# Qualidade de codigo
lint: ## Executa linters (Ruff, Black, isort)
	@echo "Executando Ruff..."
	ruff check app/
	@echo "Verificando Black..."
	black --check app/
	@echo "Verificando isort..."
	isort --check-only app/
	@echo "Lint concluido."

format: ## Formata o codigo (Black + isort)
	@echo "Formatando com Black..."
	black app/
	@echo "Organizando imports com isort..."
	isort app/
	@echo "Formatacao concluida."

ruff-fix: ## Corrige problemas encontrados pelo Ruff
	ruff check app/ --fix

# Docker
docker-build: ## Builda a imagem Docker
	docker build -t fastapi-seminario:latest .

docker-up: ## Sobe todos os containers
	$(DOCKER_COMPOSE) up -d

docker-down: ## Para todos os containers
	$(DOCKER_COMPOSE) down

docker-restart: ## Reinicia todos os containers
	$(DOCKER_COMPOSE) restart

docker-logs: ## Exibe logs dos containers
	$(DOCKER_COMPOSE) logs -f

docker-logs-api: ## Exibe logs apenas da API
	$(DOCKER_COMPOSE) logs -f api

docker-ps: ## Lista containers em execucao
	$(DOCKER_COMPOSE) ps

docker-clean: ## Remove containers, volumes e imagens
	$(DOCKER_COMPOSE) down -v --rmi all

# Utilitarios
clean: ## Limpa arquivos temporarios
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml
	@echo "Limpeza concluida."

env-setup: ## Cria arquivo .env a partir do exemplo
	cp .env.example .env
	@echo "Arquivo .env criado. Edite conforme necessario."
