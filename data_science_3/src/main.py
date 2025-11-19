"""
NLP Sentiment Analysis API

FastAPI server for sentiment and emotion analysis.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from src.nlp_pipeline import NLPPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NLP Sentiment Analysis API",
    description="Real-time sentiment and emotion analysis using transformers",
    version="1.0.0"
)

# Initialize pipeline (lazy loading)
nlp_pipeline = None


def get_pipeline():
    """Get or initialize NLP pipeline."""
    global nlp_pipeline
    if nlp_pipeline is None:
        logger.info("Initializing NLP pipeline...")
        nlp_pipeline = NLPPipeline()
    return nlp_pipeline


class TextInput(BaseModel):
    """Single text input."""
    text: str


class BatchTextInput(BaseModel):
    """Batch text input."""
    texts: List[str]


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "NLP Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze",
            "batch": "POST /analyze/batch",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
def health():
    """Health check."""
    pipeline_loaded = nlp_pipeline is not None
    return {
        "status": "healthy" if pipeline_loaded else "initializing",
        "pipeline_loaded": pipeline_loaded
    }


@app.post("/analyze")
def analyze_text(input_data: TextInput):
    """
    Analyze sentiment and emotions for a single text.
    
    Returns sentiment label, score, and top emotions.
    """
    try:
        pipeline = get_pipeline()
        result = pipeline.analyze(input_data.text)
        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
def analyze_batch(input_data: BatchTextInput):
    """
    Analyze sentiment for multiple texts.
    
    Returns list of sentiment analysis results.
    """
    if not input_data.texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    if len(input_data.texts) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 texts per batch"
        )
    
    try:
        pipeline = get_pipeline()
        results = []
        for text in input_data.texts:
            results.append(pipeline.analyze(text))
        
        return {
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment")
def sentiment_only(input_data: TextInput):
    """Get sentiment only (faster)."""
    try:
        pipeline = get_pipeline()
        result = pipeline.sentiment_analyzer.analyze(input_data.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emotions")
def emotions_only(input_data: TextInput):
    """Get emotions only."""
    try:
        pipeline = get_pipeline()
        result = pipeline.emotion_analyzer.analyze(input_data.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
