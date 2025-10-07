"""
Industry-standard unit test suite for Flask dashboard app.
Covers all endpoints and error handling for src/app.py.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.app import app

def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_index_endpoint():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Portfolio Showcase" in response.data

def test_404():
    client = app.test_client()
    response = client.get("/notfound")
    assert response.status_code == 404
