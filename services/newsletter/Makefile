.PHONY: help install test run setup clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

setup: ## Run setup checks
	python scripts/setup.py

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

run: ## Run the development server
	python main.py

run-prod: ## Run the production server
	uvicorn app.api:app --host 0.0.0.0 --port 8000

lint: ## Run linting
	flake8 app/ tests/
	pylint app/

format: ## Format code
	black app/ tests/
	isort app/ tests/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

example: ## Run example script
	python examples/chat_example.py

docker-build: ## Build Docker image
	docker build -t ai-recipe-agent .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env ai-recipe-agent

# MongoDB Migration Commands
mongo-dump: ## Dump local MongoDB database
	./scripts/migrate_mongodb.sh dump ./mongodb_dump

mongo-restore: ## Restore MongoDB dump to cloud (usage: make mongo-restore TARGET_URI="mongodb+srv://..." TARGET_DB="dbname")
	./scripts/migrate_mongodb.sh restore ./mongodb_dump "$(TARGET_URI)" "$(TARGET_DB)"

mongo-migrate: ## Migrate local MongoDB to cloud (usage: make mongo-migrate TARGET_URI="mongodb+srv://..." TARGET_DB="dbname")
	./scripts/migrate_mongodb.sh migrate "$(TARGET_URI)" "$(TARGET_DB)" 