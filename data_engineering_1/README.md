# NYC Taxi Analytics Pipeline

A production-grade, modern data engineering portfolio project using Dagster, dbt, and DuckDB with NYC Taxi data. Demonstrates best practices in data ingestion, validation, transformation, orchestration, testing, monitoring, and CI/CD.

## Features
- Modular architecture: ingestion, validation, transformation, orchestration
- Data quality monitoring and metrics
- Type safety, linting, and code formatting
- Unit and integration tests
- CI/CD pipeline (GitHub Actions)
- Dockerized local development
- dbt models for analytics

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

## Data Sources
- NYC Taxi & Limousine Commission Open Data
- Zone lookup tables

## Roadmap
- [x] Modular ingestion, validation, transformation
- [x] Data quality monitoring
- [x] dbt analytics models
- [x] CI/CD pipeline
- [ ] Add Airbyte for ELT
- [ ] Add ML models for fare prediction
- [ ] Add dashboard for analytics

## Versioning
- Semantic versioning: see `pyproject.toml` and `dbt_project.yml`
- Releases tracked in GitHub

## License
MIT

---

For full code and configuration, see project files. This README summarizes the deployment and usage steps.