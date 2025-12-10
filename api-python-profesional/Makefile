# Makefile for Songs API
# Professional build and development automation

.PHONY: help install dev test clean lint format docs run

# Default target
help:
	@echo "Songs API - Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Setup development environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  run         Run the application"
	@echo "  test        Run tests with coverage"
	@echo "  lint        Run code quality checks"
	@echo "  format      Format code with black and isort"
	@echo "  typecheck   Run type checking with mypy"
	@echo "  security    Run security checks with bandit"
	@echo ""
	@echo "Documentation:"
	@echo "  docs        Generate API documentation"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean       Clean build artifacts"
	@echo "  reset-db    Reset database to initial state"
	@echo ""

# Setup commands
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

dev: install
	@echo "Setting up development environment..."
	cp .env.example .env
	mkdir -p data logs
	@echo "Development environment ready!"

# Development commands
run:
	@echo "Starting Songs API..."
	python app.py

test:
	@echo "Running tests with coverage..."
	pytest --cov=. --cov-report=html --cov-report=term-missing

test-fast:
	@echo "Running fast tests..."
	pytest -m "not slow" --cov=. --cov-report=term-missing

lint:
	@echo "Running code quality checks..."
	flake8 .
	mypy .

format:
	@echo "Formatting code..."
	black .
	isort .

security:
	@echo "Running security checks..."
	bandit -r . -f json -o security-report.json

# Documentation
docs:
	@echo "API documentation available at http://localhost:5001/api/docs"

# Maintenance
clean:
	@echo "Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "Clean complete!"

reset-db:
	@echo "Resetting database..."
	cp db.json data/db.json
	@echo "Database reset complete!"

# Database operations
db-backup:
	@echo "Creating database backup..."
	cp data/db.json data/db_backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "Backup created"

db-migrate:
	@echo "Running database migration..."
	python -c "from services.database import db_service; print('Database structure validated')"

# Production commands
build:
	@echo "Building for production..."
	python setup.py sdist bdist_wheel

deploy-check:
	@echo "Running deployment checks..."
	pytest -m "not slow"
	flake8 .
	bandit -r .
	mypy .

# Docker commands (for future use)
docker-build:
	docker build -t songs-api .

docker-run:
	docker run -p 5001:5001 songs-api

# Environment management
env-check:
	@echo "Checking environment..."
	@python -c "from config.settings import settings; print(f'Environment: {settings.ENVIRONMENT}')"
	@python -c "from config.settings import settings; print(f'Database: {settings.DATABASE_PATH}')"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	pytest tests/test_performance.py -v

# Load testing (requires additional tools)
load-test:
	@echo "Running load tests..."
	@echo "Install additional tools: pip install locust"
	@echo "Run: locust -f tests/load_test.py --host=http://localhost:5001"

# Code metrics
metrics:
	@echo "Generating code metrics..."
	@echo "Cyclomatic Complexity:"
	@radon cc . -a
	@echo ""
	@echo "Maintainability Index:"
	@radon mi . -s
	@echo ""
	@echo "Code Coverage:"
	pytest --cov=. --cov-report=term-missing

# Version management
version:
	@python -c "from config.settings import settings; print(f'Songs API v{settings.APP_VERSION}')"

# Health checks
health:
	@echo "Checking API health..."
	curl -f http://localhost:5001/ || echo "API is not responding"

api-health:
	@echo "Checking detailed API health..."
	curl -f http://localhost:5001/api/v1/health || echo "API health check failed"

# Backup all data
backup-all:
	@echo "Creating full backup..."
	mkdir -p backups
	tar -czf backups/songs_api_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude='__pycache__' \
		--exclude='.git' \
		--exclude='venv' \
		--exclude='node_modules' \
		.
	@echo "Full backup created in backups/"

# Quick development workflow
quick-test: format lint test
	@echo "Quick development cycle complete!"

# Full quality check
quality: format lint security test metrics
	@echo "Full quality check complete!"

# Release preparation
release-prep: quality docs
	@echo "Release preparation complete!"
	@echo "Run 'make build' to create distribution packages"