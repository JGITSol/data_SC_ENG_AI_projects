# Specsheet: data_engineering_4

## Title
Cloud-Native Streaming Data Platform for Smart Cities

## Objective
Build a scalable, cloud-native data engineering platform for ingesting, processing, and analyzing real-time urban sensor data (traffic, air quality, public transport) using modern streaming and cloud technologies.

## Tech Stack
- Python (FastAPI, Kafka, Spark Streaming)
- PostgreSQL, Redis, S3 (object storage)
- Docker, Docker Compose, Kubernetes (deployment)
- Terraform/Bicep (IaC)
- GitHub Actions (CI/CD)
- Prometheus, Grafana (monitoring)
- OAuth2/JWT (security)
- dbt (transformations)

## Core Features
- Real-time ingestion from multiple sources (Kafka topics, REST, MQTT)
- Stream processing (Spark Streaming): filtering, aggregation, anomaly detection
- Batch ETL for historical data
- Data lake integration (S3)
- REST API for querying processed data (FastAPI, OpenAPI docs)
- Health, diagnostics, metrics endpoints
- Automated tests (unit, integration, E2E)
- CI/CD pipeline, containerized deployment
- Monitoring, alerting, logging
- Secure authentication (OAuth2/JWT)
- Infrastructure as Code for cloud deployment

## Deliverables
- Source code (src/, tests/, Dockerfile, docker-compose.yml, k8s manifests)
- Terraform/Bicep scripts
- API documentation (OpenAPI)
- Architecture diagrams
- README with setup, usage, and cloud deployment instructions

---

# Specsheet: data_science_4

## Title
End-to-End ML Platform for Urban Quality of Life Forecasting

## Objective
Develop a robust, production-ready ML platform for forecasting urban quality of life metrics using multi-source data, advanced modeling, and cloud deployment.

## Tech Stack
- Python (FastAPI, scikit-learn, XGBoost, PyTorch/TensorFlow)
- Jupyter Notebooks (EDA, prototyping)
- MLflow (model tracking, registry)
- PostgreSQL, S3 (data storage)
- Docker, Docker Compose, Kubernetes
- GitHub Actions (CI/CD)
- Prometheus, Grafana (monitoring)
- OAuth2/JWT (security)
- React or Dash (SPA dashboard)

## Core Features
- Data ingestion, cleaning, feature engineering (scripts, notebooks)
- Advanced ML models (ensemble, deep learning)
- Model training, evaluation, explainability (SHAP, LIME)
- Model serving API (FastAPI, OpenAPI docs)
- Automated retraining pipeline (MLflow, Airflow/Dagster)
- Interactive dashboard (React/Dash) for predictions, EDA, monitoring
- Health, diagnostics, metrics endpoints
- Automated tests (unit, integration, E2E)
- CI/CD pipeline, containerized deployment
- Monitoring, alerting, logging
- Secure authentication (OAuth2/JWT)
- Cloud deployment (Kubernetes, S3, managed DB)

## Deliverables
- Source code (src/, tests/, notebooks/, Dockerfile, docker-compose.yml, k8s manifests)
- MLflow tracking setup
- API documentation (OpenAPI)
- Dashboard source
- Architecture diagrams
- README with setup, usage, and cloud deployment instructions
