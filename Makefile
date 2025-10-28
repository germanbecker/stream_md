.PHONY: help install install-dev test test-cov lint format clean build upload docs

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=stream_md --cov-report=html --cov-report=term-missing

lint:  ## Run linting
	flake8 src tests examples
	mypy src

format:  ## Format code
	black src tests examples
	isort src tests examples

format-check:  ## Check code formatting
	black --check src tests examples
	isort --check-only src tests examples

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

upload-test:  ## Upload to test PyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

check-all: format-check lint test  ## Run all checks