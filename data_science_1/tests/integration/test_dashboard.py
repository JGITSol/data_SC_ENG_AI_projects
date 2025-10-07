"""
Integration test for dashboard root endpoint.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.app import app

def test_index_endpoint():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Portfolio Showcase" in response.data
