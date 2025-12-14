.PHONY: install test lint format clean

install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/

format:
	black src/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
