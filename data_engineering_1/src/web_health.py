"""
Industry-standard health/diagnostics endpoint for Dagster pipeline container.
Exposes /health and /diagnostics using FastAPI, referencing best practices from Dagster, dbt, and ML orchestration projects.
"""
from fastapi import FastAPI
from dagster import DagsterInstance
import pkg_resources

app = FastAPI()

@app.get("/health")
def health():
    try:
        instance = DagsterInstance.get()
        dagster_version = pkg_resources.get_distribution("dagster").version
        return {
            "status": "ok",
            "dagster_instance_type": str(type(instance)),
            "dagster_version": dagster_version,
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/diagnostics")
def diagnostics():
    # Add more detailed diagnostics if needed
    return {"status": "ok", "message": "Diagnostics endpoint is working."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
