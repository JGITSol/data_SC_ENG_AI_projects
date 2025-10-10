# Cloud-Native Streaming Data Platform for Smart Cities

This project ingests, processes, and exposes real-time urban sensor data using FastAPI, Kafka, Spark Streaming, PostgreSQL, Redis, and S3. It is containerized and ready for cloud deployment.

## Quickstart
1. Build and run containers:
   ```bash
   cd data_engineering_4
   docker-compose up --build
   ```
2. API endpoints:
   - `/health` — health check
   - `/ingest` — ingest test data
   - `/query` — query processed data

## Stack
- Python (FastAPI, Kafka, Spark Streaming)
- PostgreSQL, Redis, S3
- Docker, Docker Compose
- Automated tests (pytest)

## Structure
- `src/` — main code
- `tests/` — unit/integration tests
- `Dockerfile`, `docker-compose.yml`
- `README.md`, `requirements.txt`, `pyproject.toml`
