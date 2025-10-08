from fastapi.testclient import TestClient
from src.main import app
import json
import os

def test_predict():
    client = TestClient(app)
    sample_path = os.path.join(os.path.dirname(__file__), '../notebooks/sample_input.json')
    with open(sample_path, 'r') as f:
        sample = json.load(f)
    response = client.post("/predict", json=sample)
    assert response.status_code == 200
    result = response.json()
    assert "predictions" in result
    assert isinstance(result["predictions"], list)
    assert len(result["predictions"]) == len(sample)
