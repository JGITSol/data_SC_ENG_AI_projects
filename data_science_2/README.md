# data_science_2

## Predictive Analytics Platform for Urban Quality of Life

**Tech Stack:** Python (Flask or FastAPI, scikit-learn, XGBoost, pandas, numpy), Jupyter Notebooks, MLflow, PostgreSQL, Docker, pytest, coverage, Vue.js/React dashboard, Plotly/Dash

### Features
- Data ingestion, cleaning, EDA
- Predictive models (regression/classification)
- Model serving API (Flask/FastAPI)
- Interactive dashboard
- Health/diagnostics endpoints
- Automated tests (pytest), coverage >90%
- CI/CD pipeline, containerized deployment

### Structure
- `src/` — main code
- `tests/` — unit/integration tests
- `notebooks/` — EDA/modeling
- `Dockerfile`, `docker-compose.yml`
- `requirements.txt`, `pyproject.toml`

---

## Quickstart
```bash
# Build and run
cd data_science_2
docker-compose up --build
```

## API Docs
- `/health` — health check
- `/predict` — model predictions

## License
MIT
