from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import router as api_router
import os

app = FastAPI(title="Urban Quality of Life Analytics")

app.include_router(api_router)

dashboard_dir = os.path.join(os.path.dirname(__file__), "..", "dashboard")
if os.path.isdir(dashboard_dir):
    app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")

@app.get("/health")
def health():
    return {"status": "ok"}
