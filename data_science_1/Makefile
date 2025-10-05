.PHONY: install lint test clean format type-check all

install:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src/ tests/
	black --check src/ tests/

format:
	ruff check --fix src/ tests/
	black src/ tests/

type-check:
	mypy src/

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -m integration

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	rm -rf build dist *.egg-info

all: clean install lint type-check test
