"""
Quality of Life Prediction API

FastAPI server providing ML predictions for city quality of life scores.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import logging

from src.ml_pipeline import QualityOfLifePredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quality of Life Prediction API",
    description="ML-powered API for predicting city quality of life scores",
    version="1.0.0"
)

# Initialize predictor
predictor = QualityOfLifePredictor()

# Load model if it exists
model_path = Path("models/quality_of_life_model.joblib")
if model_path.exists():
    try:
        predictor.load_model(str(model_path))
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load model: {e}")


class CityMetrics(BaseModel):
    """Input features for quality prediction."""
    cost_of_living_index: float = Field(..., ge=0, le=200, description="Cost of living index")
    rent_index: float = Field(..., ge=0, le=150, description="Rent index")
    safety_index: float = Field(..., ge=0, le=100, description="Safety index")
    health_care_index: float = Field(..., ge=0, le=100, description="Healthcare quality index")
    pollution_index: float = Field(..., ge=0, le=100, description="Pollution index")
    climate_index: float = Field(..., ge=0, le=100, description="Climate index")
    traffic_time_index: float = Field(..., ge=0, le=200, description="Traffic time index")
    purchasing_power_index: float = Field(..., ge=0, le=200, description="Purchasing power index")


class PredictionResponse(BaseModel):
    """Prediction response."""
    quality_score: float
    features: Dict[str, float]
    model_metadata: Optional[Dict[str, Any]] = None


class TrainingRequest(BaseModel):
    """Request to train/retrain model."""
    n_samples: int = Field(500, ge=100, le=10000)
    model_type: str = Field("random_forest", regex="^(random_forest|gradient_boosting)$")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Quality of Life Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    model_loaded = predictor.model is not None
    
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "model_metadata": predictor.model_metadata if model_loaded else None
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(metrics: CityMetrics):
    """
    Predict quality of life score for a city.
    
    Args:
        metrics: City metrics (cost of living, safety, healthcare, etc.)
        
    Returns:
        Predicted quality score and metadata
    """
    if predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Train a model first using /train endpoint."
        )
    
    try:
        # Convert to DataFrame
        input_df = pd.DataFrame([metrics.dict()])
        
        # Make prediction
        prediction = predictor.predict(input_df)[0]
        
        return PredictionResponse(
            quality_score=round(float(prediction), 2),
            features=metrics.dict(),
            model_metadata={
                "model_type": predictor.model_metadata.get("model_type"),
                "trained_at": predictor.model_metadata.get("trained_at")
            }
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch")
def predict_batch(cities: List[CityMetrics]):
    """
    Predict quality scores for multiple cities.
    
    Args:
        cities: List of city metrics
        
    Returns:
        List of predictions
    """
    if predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Train a model first."
        )
    
    try:
        # Convert to DataFrame
        input_df = pd.DataFrame([city.dict() for city in cities])
        
        # Make predictions
        predictions = predictor.predict(input_df)
        
        return {
            "predictions": [
                {
                    "quality_score": round(float(pred), 2),
                    "features": city.dict()
                }
                for pred, city in zip(predictions, cities)
            ],
            "count": len(predictions)
        }
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
def train_model(request: TrainingRequest):
    """
    Train or retrain the ML model.
    
    Args:
        request: Training configuration
        
    Returns:
        Training metrics and model info
    """
    try:
        logger.info(f"Training model with {request.n_samples} samples...")
        
        # Generate synthetic data
        df = predictor.generate_synthetic_data(n_samples=request.n_samples)
        
        # Train model
        metrics = predictor.train(df, model_type=request.model_type)
        
        # Save model
        model_path = predictor.save_model()
        
       return {
            "status": "success",
            "message": f"Model trained successfully",
            "model_path": str(model_path),
            "metrics": {
                "test_r2": round(metrics['test_r2'], 4),
                "test_rmse": round(metrics['test_rmse'], 4),
                "test_mae": round(metrics['test_mae'], 4),
                "cv_r2": f"{metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}"
            },
            "model_type": request.model_type,
            "n_samples": request.n_samples
        }
    
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features/importance")
def get_feature_importance():
    """Get feature importance from trained model."""
    if predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    try:
        importance_df = predictor.get_feature_importance()
        
        if importance_df.empty:
            raise HTTPException(
                status_code=400,
                detail="Model does not support feature importance"
            )
        
        return {
            "features": importance_df.to_dict(orient='records')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
def get_model_info():
    """Get information about the loaded model."""
    if predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    return {
        "model_loaded": True,
        "metadata": predictor.model_metadata,
        "feature_names": predictor.feature_names
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
