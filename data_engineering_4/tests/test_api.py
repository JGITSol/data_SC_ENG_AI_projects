from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ingest():
    payload = {"data": {"sensor": "temp", "value": 22.5}}
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["received"] == payload["data"]

def test_query():
    response = client.get("/query")
    assert response.status_code == 200
    assert "result" in response.json()
    assert isinstance(response.json()["result"], list)
