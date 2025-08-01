.PHONY: help install test run setup clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-webapp: ## Install webapp dependencies
	cd webapp && npm install

install-all: install install-webapp ## Install all dependencies (Python + Node.js)

setup: ## Run setup checks
	python scripts/setup.py

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

test-webapp: ## Run webapp tests
	cd webapp && npm test

lint: ## Run linting
	flake8 app/ tests/
	pylint app/

lint-webapp: ## Run webapp linting
	cd webapp && npm run lint

format: ## Format code
	black app/ tests/
	isort app/

format-webapp: ## Format webapp code
	cd webapp && npm run format

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-webapp: ## Clean webapp build files
	cd webapp && rm -rf build/ dist/ .svelte-kit/

clean-all: clean clean-webapp ## Clean all generated files

# MongoDB Migration Commands
mongo-dump: ## Dump local MongoDB database
	./scripts/migrate_mongodb.sh dump ./mongodb_dump

mongo-restore: ## Restore MongoDB dump to cloud (usage: make mongo-restore TARGET_URI="mongodb+srv://..." TARGET_DB="dbname")
	./scripts/migrate_mongodb.sh restore ./mongodb_dump "$(TARGET_URI)" "$(TARGET_DB)"

mongo-migrate: ## Migrate local MongoDB to cloud (usage: make mongo-migrate TARGET_URI="mongodb+srv://..." TARGET_DB="dbname")
	./scripts/migrate_mongodb.sh migrate "$(TARGET_URI)" "$(TARGET_DB)"

# Deployment Commands
deploy-api: ## Deploy API to Railway
	./scripts/deploy.sh railway

deploy-webapp: ## Deploy webapp to Vercel (requires Vercel CLI)
	./scripts/deploy.sh vercel

deploy-all: ## Deploy both API and webapp to Railway
	./scripts/deploy.sh all

# Development Commands
dev: ## Run both API and webapp in development mode
	@echo "Starting API server..."
	@./venv/bin/python main.py &
	@echo "Starting webapp..."
	@cd webapp && npm run dev &
	@echo "API: http://localhost:8000"
	@echo "Webapp: http://localhost:3000"
	@echo "Press Ctrl+C to stop both servers"

# Build Commands
build-webapp: ## Build webapp for production
	cd webapp && npm run build

build-all: build-webapp ## Build all components for production

# Health Checks
health-api: ## Check API health
	curl -f http://localhost:8000/ || echo "API is not running"

health-webapp: ## Check webapp health
	curl -f http://localhost:3000/ || echo "Webapp is not running"

health: health-api health-webapp ## Check health of all services