# SOTA Data Science Portfolio Project

A production-grade, modern data science portfolio project with ML pipeline, dashboard, and experiment tracking. Demonstrates best practices in data ingestion, validation, feature engineering, modeling, monitoring, and CI/CD.

## Architecture

- **Python**: ML pipeline, data processing, dashboard
- **DuckDB**: Analytical database for local development
- **MLflow**: Experiment tracking
- **Docker Compose**: Local orchestration of services
- **CI/CD**: Automated lint, type-check, test, build, and artifact upload via GitHub Actions

## Features

- Modular ML pipeline: ingestion, validation, feature engineering, modeling, evaluation
- Dashboard for analytics and model results
- Experiment tracking with MLflow
- Data quality monitoring and metrics
- Type safety, linting, and code formatting
- Unit and integration tests (pytest)
- CI/CD pipeline (GitHub Actions)
- Dockerized local development
- Structured logging

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- MLflow (installed via pip)

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/sota-ds-portfolio.git
cd sota-ds-portfolio

# Install dependencies
pip install -e ".[dev]"
pre-commit install

# Start dashboard locally
python src/app.py

# Start MLflow tracking server
mlflow ui
```

### Docker Compose

```bash
docker-compose up --build
```

### Run Tests & Lint

```bash
make lint
make test
make type-check
```

## ML Pipeline & API

- **Ingestion**: Load and validate data from public sources
- **Feature Engineering**: Create features for modeling
- **Modeling**: Train, evaluate, and track models
- **Dashboard**: Visualize analytics and model results
- **Monitoring**: Data quality metrics, logging, and pipeline health

## Testing

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Run all tests: `make test`
- Coverage uploaded to Codecov in CI

## Deployment & CI/CD

- GitHub Actions workflow: `.github/workflows/ci.yml`
  - Lint, type-check, test, build, upload artifacts
  - Matrix testing for Python 3.10, 3.11, 3.12
- Docker Compose for local orchestration

## Monitoring & Validation

- Data quality metrics (completeness, validity, overall score)
- Structured logging for pipeline events
- Validation results and warnings in dashboard and MLflow

## Roadmap

- [x] Modular ML pipeline
- [x] Dashboard for analytics
- [x] MLflow experiment tracking
- [x] CI/CD pipeline
- [x] Integration tests
- [ ] Add advanced ML models
- [ ] Add real-time inference API
- [ ] Add interactive analytics dashboard

## Versioning

- Semantic versioning: see `pyproject.toml`
- Releases tracked in GitHub

## License
MIT

---

For full code and configuration, see project files. This README summarizes the deployment and usage steps for portfolio showcase.
