"""
MLOps API - Model Training and Serving

FastAPI service for model lifecycle management.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
import logging

from src.mlops_platform import MLOpsExperiment, ModelMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MLOps Platform API",
    description="Model lifecycle management with experiment tracking",
    version="1.0.0"
)

# Global state
experiment = MLOpsExperiment("api-models")
monitor = ModelMonitor()
current_model = None


class TrainRequest(BaseModel):
    """Model training request."""
    model_type: str = "random_forest"
    n_samples: int = 1000
    n_features: int = 20


class PredictRequest(BaseModel):
    """Prediction request."""
    features: List[List[float]]


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "MLOps Platform API",
        "version": "1.0.0",
        "endpoints": {
            "train": "POST /train",
            "predict": "POST /predict",
            "models": "GET /models",
            "metrics": "GET /metrics",
            "health": "GET /health"
        }
    }


@app.get("/health")
def health():
    """Health check."""
    return {
        "status": "healthy",
        "model_loaded": current_model is not None,
        "predictions_logged": len(monitor.predictions_log)
    }


@app.post("/train")
def train_model(request: TrainRequest):
    """
    Train a new model.
    
    Trains model with MLflow tracking and returns metrics.
    """
    global current_model
    
    if request.model_type not in ["random_forest", "gradient_boosting"]:
        raise HTTPException(
            status_code=400,
            detail="model_type must be 'random_forest' or 'gradient_boosting'"
        )
    
    try:
        logger.info(f"Training {request.model_type}...")
        
        model, metrics = experiment.train_model(
            model_type=request.model_type,
            n_samples=request.n_samples,
            n_features=request.n_features
        )
        
        # Update current model
        current_model = model
        
        return {
            "status": "success",
            "model_type": request.model_type,
            "metrics": {
                "test_accuracy": round(metrics["test_accuracy"], 4),
                "test_f1": round(metrics["test_f1"], 4),
                "cv_accuracy": f"{metrics['cv_accuracy_mean']:.4f} ± {metrics['cv_accuracy_std']:.4f}"
            }
        }
    
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
def predict(request: PredictRequest):
    """
    Make predictions using current model.
    
    Returns predictions and logs them for monitoring.
    """
    if current_model is None:
        raise HTTPException(
            status_code=503,
            detail="No model loaded. Train a model first."
        )
    
    try:
        features_array = np.array(request.features)
        predictions = current_model.predict(features_array)
        
        # Log predictions for monitoring
        for features, pred in zip(features_array, predictions):
            monitor.log_prediction(features, pred)
        
        return {
            "predictions": predictions.tolist(),
            "count": len(predictions)
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
def list_models():
    """
    List all trained models with metrics.
    
    Returns comparison of all models in the experiment.
    """
    try:
        comparison = experiment.compare_models()
        
        if comparison.empty:
            return {"models": [], "count": 0}
        
        models = comparison.to_dict(orient="records")
        
        return {
            "models": models,
            "count": len(models)
        }
    
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/best")
def get_best_model():
    """
    Get information about the best model.
    
    Returns best model based on test accuracy.
    """
    try:
        _, best_run = experiment.get_best_model()
        
        return {
            "run_id": best_run["run_id"],
            "model_type": best_run.get("params.model_type", "unknown"),
            "metrics": {
                "test_accuracy": best_run.get("metrics.test_accuracy"),
                "test_f1": best_run.get("metrics.test_f1"),
                "cv_accuracy": best_run.get("metrics.cv_accuracy_mean")
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting best model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def get_metrics():
    """
    Get monitoring metrics.
    
    Returns performance metrics from logged predictions.
    """
    metrics = monitor.get_performance_metrics()
    return metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)
