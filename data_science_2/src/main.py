from fastapi import FastAPI
from src.api import router as api_router

app = FastAPI(title="Urban Quality of Life Analytics")

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}
