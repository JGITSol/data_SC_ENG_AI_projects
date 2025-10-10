from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="Smart City Streaming Data Platform")

# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

# Ingest endpoint (stub for MVP)
class IngestPayload(BaseModel):
    data: dict

@app.post("/ingest")
def ingest(payload: IngestPayload):
    # Simulate streaming ingest (MVP: just echo)
    return {"received": payload.data}

# Query endpoint (stub for MVP)
@app.get("/query")
def query():
    # Simulate query (MVP: return static data)
    return {"result": [{"city": "Warsaw", "population": 1800000}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
