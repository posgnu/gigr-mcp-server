.PHONY: help install install-dev clean test test-cov lint format type-check security docs serve-docs build docker-build docker-run pre-commit setup

# Variables
PYTHON := python3
POETRY := poetry
PROJECT_NAME := project-name
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(POETRY) install --only main

install-dev: ## Install all dependencies including dev
	@echo "$(GREEN)Installing all dependencies...$(NC)"
	$(POETRY) install

setup: install-dev ## Complete development setup
	@echo "$(GREEN)Setting up development environment...$(NC)"
	$(POETRY) run pre-commit install
	@echo "$(GREEN)Setup complete!$(NC)"

clean: ## Clean up generated files
	@echo "$(RED)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	$(POETRY) run pytest $(TEST_DIR) -v

test-cov: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(POETRY) run pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	$(POETRY) run ptw $(TEST_DIR) -- -v

test-unit: ## Run unit tests only
	@echo "$(GREEN)Running unit tests...$(NC)"
	$(POETRY) run pytest $(TEST_DIR) -v -m unit

test-integration: ## Run integration tests only
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(POETRY) run pytest $(TEST_DIR) -v -m integration

lint: ## Run all linting checks
	@echo "$(GREEN)Running linting checks...$(NC)"
	$(POETRY) run black --check $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort --check-only $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run flake8 $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run ruff check $(SRC_DIR) $(TEST_DIR)

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	$(POETRY) run black $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run ruff check --fix $(SRC_DIR) $(TEST_DIR)

type-check: ## Run type checking with mypy
	@echo "$(GREEN)Running type checking...$(NC)"
	$(POETRY) run mypy $(SRC_DIR)

security: ## Run security checks with bandit
	@echo "$(GREEN)Running security checks...$(NC)"
	$(POETRY) run bandit -r $(SRC_DIR) -ll

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	$(POETRY) run pre-commit run --all-files

quality: lint type-check security ## Run all code quality checks

ci: quality test ## Run CI pipeline locally

docs: ## Build documentation
	@echo "$(GREEN)Building documentation...$(NC)"
	$(POETRY) run sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build

serve-docs: docs ## Build and serve documentation
	@echo "$(GREEN)Serving documentation at http://localhost:8000...$(NC)"
	cd $(DOCS_DIR)/_build && $(PYTHON) -m http.server

build: clean ## Build distribution packages
	@echo "$(GREEN)Building distribution packages...$(NC)"
	$(POETRY) build

publish: build ## Publish to PyPI
	@echo "$(GREEN)Publishing to PyPI...$(NC)"
	$(POETRY) publish

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

docker-run: ## Run Docker container
	@echo "$(GREEN)Running Docker container...$(NC)"
	docker run -it --rm $(PROJECT_NAME):latest

docker-shell: ## Run Docker container with shell
	@echo "$(GREEN)Running Docker container shell...$(NC)"
	docker run -it --rm --entrypoint /bin/bash $(PROJECT_NAME):latest

update-deps: ## Update dependencies
	@echo "$(GREEN)Updating dependencies...$(NC)"
	$(POETRY) update

lock-deps: ## Lock dependencies
	@echo "$(GREEN)Locking dependencies...$(NC)"
	$(POETRY) lock --no-update

shell: ## Start poetry shell
	@echo "$(GREEN)Starting poetry shell...$(NC)"
	$(POETRY) shell

run: ## Run the main application
	@echo "$(GREEN)Running application...$(NC)"
	$(POETRY) run python -m $(SRC_DIR).main

watch: ## Watch for file changes and run tests
	@echo "$(GREEN)Watching for changes...$(NC)"
	$(POETRY) run watchmedo auto-restart -d $(SRC_DIR) -p "*.py" --recursive -- python -m $(SRC_DIR).main
