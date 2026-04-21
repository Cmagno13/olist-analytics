# ============================================================
# Olist Analytics — Makefile
# Rode "make help" para ver todos os comandos disponíveis
# ============================================================

.PHONY: help setup venv install download load validate test clean superset-up superset-down lint format

# ---------- Configuração ----------
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PY := $(VENV_BIN)/python

# ---------- Help (comando padrão) ----------
help: ## Mostra este menu de ajuda
	@echo ""
	@echo "🛒 Olist Analytics — Comandos disponíveis"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---------- Setup do ambiente ----------
setup: venv install ## Cria venv e instala todas as dependências

venv: ## Cria o ambiente virtual Python
	@echo "🐍 Criando ambiente virtual..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Venv criado em $(VENV)"

install: ## Instala as dependências do requirements.txt
	@echo "📦 Instalando dependências..."
	$(PIP) install --upgrade pip
	$(PIP) install -r infra/requirements.txt
	@echo "✅ Dependências instaladas"

# ---------- Pipeline de dados ----------
download: ## Baixa o dataset Olist do Kaggle
	@echo "⬇️  Baixando dataset Olist..."
	$(PY) ingestion/download_data.py

load: ## Carrega os CSVs no DuckDB
	@echo "📥 Carregando CSVs no DuckDB..."
	$(PY) ingestion/load_to_duckdb.py

validate: ## Roda os testes de qualidade de dados
	@echo "🔍 Validando qualidade dos dados..."
	$(PY) ingestion/validators.py

# ---------- Pipeline completo ----------
pipeline: download load validate ## Executa o pipeline completo (download → load → validate)
	@echo "🎉 Pipeline executado com sucesso!"

# ---------- Qualidade de código ----------
lint: ## Checa qualidade do código Python
	@echo "🔎 Verificando código..."
	$(VENV_BIN)/ruff check .

format: ## Formata código Python automaticamente
	@echo "🎨 Formatando código..."
	$(VENV_BIN)/ruff format .

test: ## Roda os testes automatizados (pytest)
	@echo "🧪 Rodando testes..."
	$(VENV_BIN)/pytest -v

# ---------- Superset (Docker) ----------
superset-up: ## Sobe o Apache Superset via Docker
	@echo "🚀 Subindo Superset..."
	cd infra && docker compose up -d
	@echo "✅ Superset rodando em http://localhost:8088"

superset-down: ## Para o Apache Superset
	@echo "⏹️  Parando Superset..."
	cd infra && docker compose down

superset-logs: ## Mostra logs do Superset
	cd infra && docker compose logs -f

# ---------- Limpeza ----------
clean: ## Remove arquivos temporários e caches
	@echo "🧹 Limpando arquivos temporários...
