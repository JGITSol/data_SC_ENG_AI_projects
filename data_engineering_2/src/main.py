from fastapi import FastAPI
from src.api import router as api_router

app = FastAPI(title="Urban Mobility Pipeline")

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}
