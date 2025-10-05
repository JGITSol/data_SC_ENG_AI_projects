"""
Integration test for dashboard root endpoint.
"""
from src.app import app

def test_index_endpoint():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Portfolio Showcase" in response.data
