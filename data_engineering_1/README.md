# NYC Taxi Analytics Pipeline

A SOTA, production-grade data engineering portfolio project using Dagster, dbt, and DuckDB with NYC Taxi data. This project demonstrates best practices in data ingestion, validation, transformation, orchestration, testing, monitoring, and CI/CD for modern data engineering.

## Architecture
- **Dagster**: Orchestrates the pipeline (ingestion, validation, transformation)
- **dbt**: Analytics models and transformations
- **DuckDB**: Analytical database for local development
- **Docker Compose**: Local orchestration of services
- **CI/CD**: Automated lint, type-check, test, build, and artifact upload via GitHub Actions

## Features
- Modular pipeline: ingestion, validation, transformation, orchestration
- Data quality monitoring and metrics
- Type safety, linting, and code formatting
- Unit and integration tests (pytest)
- CI/CD pipeline (GitHub Actions)
- Dockerized local development
- dbt models for analytics
- Structured logging (structlog)

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- dbt (installed via pip)
- Dagster (installed via pip)

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/nyc-taxi-analytics-pipeline.git
cd nyc-taxi-analytics-pipeline

# Install dependencies
pip install -e ".[dev]"
pre-commit install

# Start Dagster locally
dagster dev

# Run dbt models
cd dbt_project && dbt run
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

## API & Pipeline
- **Ingestion**: Extracts NYC Taxi and zone data from public sources
- **Validation**: Validates schema, types, business rules, and data quality
- **Transformation**: Cleans, enriches, and engineers features for analytics
- **dbt Models**: Staging and marts for analytics and reporting
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
- Validation results and warnings in Dagster asset metadata

## Roadmap
- [x] Modular ingestion, validation, transformation
- [x] Data quality monitoring
- [x] dbt analytics models
- [x] CI/CD pipeline
- [x] Integration tests
- [ ] Add Airbyte for ELT
- [ ] Add ML models for fare prediction
- [ ] Add dashboard for analytics

## Versioning
- Semantic versioning: see `pyproject.toml` and `dbt_project.yml`
- Releases tracked in GitHub

## License
MIT

---

For full code and configuration, see project files. This README summarizes the deployment and usage steps for portfolio showcase.