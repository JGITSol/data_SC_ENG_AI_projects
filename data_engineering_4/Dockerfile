# Dockerfile for data_engineering_4
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY README.md ./

EXPOSE 8000

CMD ["python", "src/main.py"]
