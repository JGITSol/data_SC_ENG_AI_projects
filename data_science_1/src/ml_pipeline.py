"""
ML Pipeline for Quality of Life Prediction

This module provides end-to-end ML pipeline for predicting quality of life scores
based on city metrics (cost of living, pollution, safety, etc.).
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityOfLifePredictor:
    """
    Machine Learning pipeline for quality of life prediction.
    
    Features:
    - Data preprocessing and feature engineering
    - Multiple model training (RandomForest, GradientBoosting)
    - Model evaluation and comparison
    - Model persistence
    - Prediction API
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize the predictor.
        
        Args:
            model_dir: Directory to save/load models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_metadata = {}
    
    def generate_synthetic_data(self, n_samples: int = 500) -> pd.DataFrame:
        """
        Generate synthetic city quality of life data.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            DataFrame with city metrics and quality scores
        """
        np.random.seed(42)
        
        # Generate features
        data = {
            'cost_of_living_index': np.random.uniform(40, 120, n_samples),
            'rent_index': np.random.uniform(15, 90, n_samples),
            'safety_index': np.random.uniform(30, 90, n_samples),
            'health_care_index': np.random.uniform(40, 95, n_samples),
            'pollution_index': np.random.uniform(20, 100, n_samples),
            ' climate_index': np.random.uniform(50, 100, n_samples),
            'traffic_time_index': np.random.uniform(20, 150, n_samples),
            'purchasing_power_index': np.random.uniform(30, 140, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate target (quality of life score)
        # Higher safety, healthcare, climate, purchasing power = higher quality
        # Lower cost, pollution, traffic = higher quality
        quality_score = (
            0.25 * df['safety_index'] +
            0.20 * df['health_care_index'] +
            0.15 * df['climate_index'] +
            0.15 * df['purchasing_power_index'] +
            0.10 * (100 - df['pollution_index']) +
            0.10 * (100 - df['cost_of_living_index']) +
            0.05 * (100 - df['traffic_time_index'])
        )
        
        # Add some noise
        quality_score += np.random.normal(0, 5, n_samples)
        quality_score = np.clip(quality_score, 0, 100)
        
        df['quality_score'] = quality_score
        
        logger.info(f"Generated {n_samples} synthetic city records")
        return df
    
    def preprocess_data(
        self,
        df: pd.DataFrame,
        fit_scaler: bool = True
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Preprocess data for training/prediction.
        
        Args:
            df: Input DataFrame
            fit_scaler: Whether to fit scaler (True for training, False for prediction)
            
        Returns:
            Tuple of (X_scaled, y)
        """
        # Separate features and target
        if 'quality_score' in df.columns:
            X = df.drop('quality_score', axis=1)
            y = df['quality_score']
        else:
            X = df
            y = None
        
        # Store feature names
        if fit_scaler:
            self.feature_names = list(X.columns)
        
        # Scale features
        if fit_scaler:
            self.scaler = StandardScaler()
            X_scaled = pd.DataFrame(
                self.scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
        else:
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Train model first.")
            X_scaled = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
        
        return X_scaled, y
    
    def train(
        self,
        df: pd.DataFrame,
        model_type: str = 'random_forest',
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Train the ML model.
        
        Args:
            df: Training DataFrame
            model_type: 'random_forest' or 'gradient_boosting'
            test_size: Test set proportion
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info(f"Training {model_type} model...")
        
        # Preprocess
        X, y = self.preprocess_data(df, fit_scaler=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Initialize model
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        metrics = {
            'train_mse': mean_squared_error(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_mse': mean_squared_error(y_test, y_pred_test),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'test_r2': r2_score(y_test, y_pred_test),
        }
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train, y_train, cv=5, scoring='r2'
        )
        metrics['cv_r2_mean'] = cv_scores.mean()
        metrics['cv_r2_std'] = cv_scores.std()
        
        # Store metadata
        self.model_metadata = {
            'model_type': model_type,
            'trained_at': datetime.utcnow().isoformat(),
            'n_samples': len(df),
            'n_features': X.shape[1],
            'feature_names': self.feature_names,
            'metrics': metrics
        }
        
        logger.info(f"Model trained successfully")
        logger.info(f"Test R²: {metrics['test_r2']:.4f}")
        logger.info(f"Test RMSE: {metrics['test_rmse']:.4f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on new data.
        
        Args:
            X: Input features
            
        Returns:
            Predicted quality scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Train model first.")
        
        X_scaled, _ = self.preprocess_data(X, fit_scaler=False)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from trained model.
        
        Returns:
            DataFrame with feature names and importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            return pd.DataFrame()
    
    def save_model(self, filename: str = None) -> Path:
        """
        Save trained model to disk.
        
        Args:
            filename: Model filename (default: model_TIMESTAMP.joblib)
            
        Returns:
            Path to saved model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"model_{timestamp}.joblib"
        
        model_path = self.model_dir / filename
        
        # Save everything needed for prediction
        save_dict = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metadata': self.model_metadata
        }
        
        joblib.dump(save_dict, model_path)
        logger.info(f"Model saved to {model_path}")
        
        return model_path
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained model from disk.
        
        Args:
            model_path: Path to model file
        """
        model_dict = joblib.load(model_path)
        
        self.model = model_dict['model']
        self.scaler = model_dict['scaler']
        self.feature_names = model_dict['feature_names']
        self.model_metadata = model_dict.get('metadata', {})
        
        logger.info(f"Model loaded from {model_path}")
        logger.info(f"Model type: {self.model_metadata.get('model_type', 'unknown')}")


def main():
    """Train and save a demo model."""
    # Initialize predictor
    predictor = QualityOfLifePredictor()
    
    # Generate synthetic data
    df = predictor.generate_synthetic_data(n_samples=500)
    
    # Train model
    metrics = predictor.train(df, model_type='random_forest')
    
    # Print results
    print("\n=== Model Training Results ===")
    print(f"Test R²: {metrics['test_r2']:.4f}")
    print(f"Test RMSE: {metrics['test_rmse']:.4f}")
    print(f"Test MAE: {metrics['test_mae']:.4f}")
    print(f"CV R² (mean ± std): {metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}")
    
    # Feature importance
    print("\n=== Feature Importance ===")
    importance_df = predictor.get_feature_importance()
    print(importance_df.to_string(index=False))
    
    # Save model
    model_path = predictor.save_model("quality_of_life_model.joblib")
    print(f"\nModel saved to: {model_path}")
    
    # Demo prediction
    print("\n=== Demo Prediction ===")
    sample = df.drop('quality_score', axis=1).iloc[:1]
    prediction = predictor.predict(sample)
    actual = df.iloc[:1]['quality_score'].values[0]
    print(f"Predicted: {prediction[0]:.2f}")
    print(f"Actual: {actual:.2f}")


if __name__ == "__main__":
    main()
