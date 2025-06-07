.PHONY: help install test lint format clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install    Install dependencies"
	@echo "  make test       Run tests"
	@echo "  make lint       Run linting"
	@echo "  make format     Format code"
	@echo "  make clean      Clean build artifacts"
	@echo "  make docker-up  Start Docker services"
	@echo "  make docker-down Stop Docker services"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest tests/ -v --cov=fraud_detection --cov-report=html

lint:
	flake8 fraud_detection/
	mypy fraud_detection/
	black --check fraud_detection/
	isort --check-only fraud_detection/

format:
	black fraud_detection/
	isort fraud_detection/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info
	rm -rf .coverage htmlcov/
	rm -rf .pytest_cache/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f fraud-detector
