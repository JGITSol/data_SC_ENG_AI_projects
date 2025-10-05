"""
Industry-standard integration test suite for Flask dashboard app.
Covers app startup, endpoint responses, and error handling for src/app.py.
"""
from multiprocessing import Process
import time
import requests
from src.app import app

def run_app():
    app.run(host="127.0.0.1", port=8081)

def test_app_integration():
    proc = Process(target=run_app)
    proc.start()
    time.sleep(2)
    try:
        r = requests.get("http://127.0.0.1:8081/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        r = requests.get("http://127.0.0.1:8081/")
        assert r.status_code == 200
        assert "Portfolio Showcase" in r.text
        r = requests.get("http://127.0.0.1:8081/notfound")
        assert r.status_code == 404
    finally:
        proc.terminate()
        proc.join()
