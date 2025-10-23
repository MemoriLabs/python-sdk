.PHONY: help dev-up dev-down dev-shell dev-build test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev-up: ## Start development environment (builds and runs containers)
	docker compose up -d --build
	@echo ""
	@echo "✓ Development environment is ready!"
	@echo "  Run 'make dev-shell' to enter the development container"
	@echo "  Run 'make test' to run tests"

dev-down: ## Stop development environment
	docker compose down

dev-shell: ## Open a shell in the development container
	docker compose exec dev /bin/bash

init-db: ## Initialize database schema for integration tests
	docker compose exec -e PYTHONPATH=/app dev python tests/database/init_db.py

dev-build: ## Rebuild the development container
	docker compose build --no-cache

test: ## Run tests in the container
	docker compose exec dev pytest

test-integration: ## Run integration tests (requires API keys and database)
	@echo "Note: Integration tests require OPENAI_API_KEY to be set"
	docker compose exec dev pytest tests/llm/clients/ -v

run-integration: ## Run integration test scripts directly (e.g., make run-integration FILE=tests/llm/clients/oss/openai/async.py)
	@echo "Running integration test: $(FILE)"
	docker compose exec -e PYTHONPATH=/app dev python $(FILE)

lint: ## Run linting (format check)
	docker compose exec dev uv run ruff check .

format: ## Format code
	docker compose exec dev uv run ruff format .

clean: ## Clean up containers, volumes, and Python cache files
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
