"""
NLP Sentiment Analysis Pipeline

Lightweight implementation using pre-trained transformers for sentiment analysis.
"""

from transformers import pipeline
import torch
import logging
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis using pre-trained DistilBERT."""
    
    def __init__(self):
        """Initialize sentiment analyzer."""
        logger.info("Loading sentiment model...")
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("Model loaded")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        if not text or len(text.strip()) == 0:
            return {"label": "NEUTRAL", "score": 0.0, "error": "Empty text"}
        
        try:
            result = self.sentiment_pipeline(text[:512])[0]
            return {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "label": result["label"],
                "score": round(result["score"], 4),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error: {e}")
            return {"label": "ERROR", "score": 0.0, "error": str(e)}
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts."""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results


class EmotionAnalyzer:
    """Emotion detection using pre-trained model."""
    
    def __init__(self):
        """Initialize emotion analyzer."""
        logger.info("Loading emotion model...")
        try:
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=3,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Emotion model loaded")
        except Exception as e:
            logger.warning(f"Emotion model unavailable: {e}")
            self.emotion_pipeline = None
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Detect emotions in text."""
        if not self.emotion_pipeline:
            return {"error": "Model not available"}
        
        try:
            results = self.emotion_pipeline(text[:512])[0]
            return {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "emotions": [
                    {"emotion": e["label"], "score": round(e["score"], 4)}
                    for e in results
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}


class NLPPipeline:
    """Complete NLP analysis pipeline."""
    
    def __init__(self):
        """Initialize pipeline."""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Run complete analysis."""
        result = {"text": text[:100] + "..." if len(text) > 100 else text}
        
        # Sentiment
        sentiment = self.sentiment_analyzer.analyze(text)
        result["sentiment"] = {
            "label": sentiment["label"],
            "score": sentiment["score"]
        }
        
        # Emotions
        emotions = self.emotion_analyzer.analyze(text)
        if "emotions" in emotions:
            result["emotions"] = emotions["emotions"]
        
        return result
