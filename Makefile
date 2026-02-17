.PHONY: build up down restart logs clean help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: down up ## Restart all services

logs: ## View logs from all services
	docker compose logs -f

logs-backend: ## View backend logs
	docker compose logs -f backend

logs-frontend: ## View frontend logs
	docker compose logs -f frontend

logs-db: ## View database logs
	docker compose logs -f db

ps: ## Show running containers
	docker compose ps

clean: ## Remove all containers, volumes, and images
	docker compose down -v
	docker rmi market-intelligence-engine-backend market-intelligence-engine-frontend || true

rebuild: clean build ## Clean and rebuild everything

shell-backend: ## Open shell in backend container
	docker compose exec backend /bin/bash

shell-db: ## Open psql shell in database
	docker compose exec db psql -U postgres -d market_intelligence
