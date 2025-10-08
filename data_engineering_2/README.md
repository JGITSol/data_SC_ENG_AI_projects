# data_engineering_2

## Real-Time Data Pipeline for Urban Mobility Analytics

**Tech Stack:** Python (FastAPI, Pandas, SQLAlchemy), Kafka, PostgreSQL, Redis, Docker, Docker Compose, pytest, coverage, dbt, Airflow/Dagster

### Features
- Real-time data ingestion via Kafka
- ETL pipeline: streaming → batch → PostgreSQL
- Data validation and quality monitoring
- REST API (FastAPI) with health/diagnostics endpoints
- Metrics (Prometheus-ready)
- Automated tests (pytest), coverage >90%
- CI/CD pipeline, containerized deployment

### Structure
- `src/` — main code
- `tests/` — unit/integration tests
- `Dockerfile`, `docker-compose.yml`
- `requirements.txt`, `pyproject.toml`
- `dbt_project/` — transformations

---

## Quickstart
```bash
# Build and run
cd data_engineering_2
docker-compose up --build
```

## API Docs
- `/health` — health check
- `/api/stream` — ingest data
- `/api/query` — query processed data

## License
MIT
