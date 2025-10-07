"""
Industry-standard health/diagnostics endpoint for Dagster pipeline container.
Exposes /health and /diagnostics using FastAPI, referencing best practices from Dagster, dbt, and ML orchestration projects.
"""
from fastapi import FastAPI
from dagster import instance_for_test
import os

app = FastAPI()

@app.get("/health")
def health():
    # Check Dagster instance health (basic check)
    try:
        dagster_home = os.environ.get("DAGSTER_HOME", ".")
        with instance_for_test(dagster_home=dagster_home) as instance:
            status = instance.info
        return {"status": "ok", "dagster": status}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/diagnostics")
def diagnostics():
    # Add more detailed diagnostics if needed
    return {"status": "ok", "message": "Diagnostics endpoint is working."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
