FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY requirements.txt ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY dbt_project/ ./dbt_project/
COPY config/ ./config/

# Create data directories
RUN mkdir -p data/raw data/processed

EXPOSE 3000

CMD ["sh", "-c", "dagster dev -h 0.0.0.0 -p 3001 & python src/web_health.py"]
