from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import router as api_router

app = FastAPI(title="Urban Quality of Life Analytics")

app.include_router(api_router)

app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/health")
def health():
    return {"status": "ok"}
