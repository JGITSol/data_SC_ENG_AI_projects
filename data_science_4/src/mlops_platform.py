"""
MLOps Platform - Model Lifecycle Management

Demonstrates model training, versioning, monitoring, and automated retraining.
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.datasets import make_classification
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any, Tuple, Optional
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLOpsExperiment:
    """
    MLOps experiment tracking with MLflow.
    """
    
    def __init__(self,experiment_name: str = "model-lifecycle"):
        """Initialize MLOps experiment."""
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        logger.info(f"Experiment: {experiment_name}")
    
    def train_model(
        self,
        model_type: str = "random_forest",
        n_samples: int = 1000,
        n_features: int = 20
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train and log model with MLflow.
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
            n_samples: Number of samples
            n_features: Number of features
            
        Returns:
            Trained model and metrics
        """
        with mlflow.start_run(run_name=f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Generate data
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_informative=15,
                n_redundant=5,
                random_state=42
            )
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Log parameters
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("n_samples", n_samples)
            mlflow.log_param("n_features", n_features)
            mlflow.log_param("test_size", 0.2)
            
            # Initialize model
            if model_type == "random_forest":
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                mlflow.log_param("n_estimators", 100)
                mlflow.log_param("max_depth", 10)
            else:
                model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
                mlflow.log_param("n_estimators", 100)
                mlflow.log_param("learning_rate", 0.1)
            
            # Train
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            metrics = {
                "train_accuracy": accuracy_score(y_train, y_pred_train),
                "test_accuracy": accuracy_score(y_test, y_pred_test),
                "test_precision": precision_score(y_test, y_pred_test),
                "test_recall": recall_score(y_test, y_pred_test),
                "test_f1": f1_score(y_test, y_pred_test)
            }
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            metrics["cv_accuracy_mean"] = cv_scores.mean()
            metrics["cv_accuracy_std"] = cv_scores.std()
            
            # Log metrics
            for name, value in metrics.items():
                mlflow.log_metric(name, value)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log feature importance if available
            if hasattr(model, 'feature_importances_'):
                importance_df = pd.DataFrame({
                    'feature': [f"feature_{i}" for i in range(n_features)],
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                importance_df.to_csv("feature_importance.csv", index=False)
                mlflow.log_artifact("feature_importance.csv")
                Path("feature_importance.csv").unlink()
            
            logger.info(f"Model trained: {model_type}")
            logger.info(f"Test Accuracy: {metrics['test_accuracy']:.4f}")
            logger.info(f"Test F1: {metrics['test_f1']:.4f}")
            
            return model, metrics
    
    def compare_models(self) -> pd.DataFrame:
        """
        Compare all models in the experiment.
        
        Returns:
            DataFrame with model comparisons
        """
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        if len(runs) == 0:
            logger.warning("No runs found")
            return pd.DataFrame()
        
        # Select relevant columns
        cols = [
            "run_id",
            "params.model_type",
            "metrics.test_accuracy",
            "metrics.test_f1",
            "metrics.cv_accuracy_mean",
            "start_time"
        ]
        
        available_cols = [c for c in cols if c in runs.columns]
        comparison = runs[available_cols].sort_values(
            "metrics.test_accuracy", ascending=False
        )
        
        return comparison
    
    def get_best_model(self, metric: str = "test_accuracy"):
        """
        Get the best model based on a metric.
        
        Args:
            metric: Metric to optimize
            
        Returns:
            Best model
        """
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric} DESC"],
            max_results=1
        )
        
        if len(runs) == 0:
            raise ValueError("No models found")
        
        best_run_id = runs.iloc[0]["run_id"]
        model_uri = f"runs:/{best_run_id}/model"
        model = mlflow.sklearn.load_model(model_uri)
        
        logger.info(f"Loaded best model (run_id: {best_run_id})")
        logger.info(f"Best {metric}: {runs.iloc[0][f'metrics.{metric}']:.4f}")
        
        return model, runs.iloc[0]


class ModelMonitor:
    """
    Monitor model performance over time.
    """
    
    def __init__(self):
        """Initialize model monitor."""
        self.predictions_log = []
    
    def log_prediction(
        self,
        features: np.ndarray,
        prediction: int,
        true_label: Optional[int] = None
    ):
        """
        Log a prediction for monitoring.
        
        Args:
            features: Input features
            prediction: Model prediction
            true_label: True label (if available)
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": int(prediction),
            "features_mean": float(features.mean()),
            "features_std": float(features.std())
        }
        
        if true_label is not None:
            log_entry["true_label"] = int(true_label)
            log_entry["correct"] = int(prediction == true_label)
        
        self.predictions_log.append(log_entry)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate performance metrics from logged predictions.
        
        Returns:
            Performance metrics
        """
        if not self.predictions_log:
            return {"error": "No predictions logged"}
        
        df = pd.DataFrame(self.predictions_log)
        
        metrics = {
            "total_predictions": len(df),
            "prediction_distribution": df["prediction"].value_counts().to_dict()
        }
        
        if "correct" in df.columns:
            metrics["accuracy"] = df["correct"].mean()
            metrics["total_correct"] = int(df["correct"].sum())
        
        return metrics


def demo():
    """Demo the MLOps platform."""
    print("=== MLOps Platform Demo ===\n")
    
    # Initialize experiment
    experiment = MLOpsExperiment("income-prediction")
    
    # Train multiple models
    print("Training models...\n")
    
    model_rf, metrics_rf = experiment.train_model("random_forest")
    model_gb, metrics_gb = experiment.train_model("gradient_boosting")
    
    # Compare models
    print("\n=== Model Comparison ===")
    comparison = experiment.compare_models()
    print(comparison.to_string(index=False))
    
    # Get best model
    print("\n=== Best Model ===")
    best_model, best_run = experiment.get_best_model()
    print(f"Model Type: {best_run['params.model_type']}")
    print(f"Test Accuracy: {best_run['metrics.test_accuracy']:.4f}")
    print(f"Test F1: {best_run['metrics.test_f1']:.4f}")
    
    # Monitor predictions
    print("\n=== Monitoring Demo ===")
    monitor = ModelMonitor()
    
    # Simulate some predictions
    X_test = np.random.randn(10, 20)
    for features in X_test:
        pred = best_model.predict([features])[0]
        true_label = np.random.choice([0, 1])
        monitor.log_prediction(features, pred, true_label)
    
    metrics = monitor.get_performance_metrics()
    print(f"Total Predictions: {metrics['total_predictions']}")
    if "accuracy" in metrics:
        print(f"Monitoring Accuracy: {metrics['accuracy']:.2%}")


if __name__ == "__main__":
    demo()
