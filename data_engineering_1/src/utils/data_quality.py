"""
Data quality monitoring and metrics calculation.
"""

from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

@dataclass
class DataQualityMetrics:
    total_records: int
    null_counts: Dict[str, int]
    null_percentages: Dict[str, float]
    duplicate_count: int
    completeness_score: float
    validity_score: float
    overall_score: float

class DataQualityMonitor:
    def __init__(self) -> None:
        logger.info("Initialized DataQualityMonitor")
    def calculate_metrics(self, df: pd.DataFrame) -> DataQualityMetrics:
        logger.info(f"Calculating data quality metrics for {len(df)} records")
        null_counts = df.isnull().sum().to_dict()
        null_percentages = (df.isnull().sum() / len(df) * 100).to_dict()
        duplicate_count = df.duplicated().sum()
        completeness_score = 100 - (sum(null_percentages.values()) / len(df.columns))
        validity_score = self._calculate_validity_score(df)
        overall_score = (completeness_score * 0.6 + validity_score * 0.4)
        metrics = DataQualityMetrics(
            total_records=len(df),
            null_counts={k: int(v) for k, v in null_counts.items()},
            null_percentages={k: round(v, 2) for k, v in null_percentages.items()},
            duplicate_count=int(duplicate_count),
            completeness_score=round(completeness_score, 2),
            validity_score=round(validity_score, 2),
            overall_score=round(overall_score, 2),
        )
        logger.info(
            "Data quality metrics calculated",
            extra={
                "overall_score": metrics.overall_score,
                "completeness": metrics.completeness_score,
                "validity": metrics.validity_score,
            },
        )
        return metrics
    def _calculate_validity_score(self, df: pd.DataFrame) -> float:
        violations = 0
        total_checks = 0
        if "fare_amount" in df.columns:
            violations += (df["fare_amount"] < 0).sum()
            total_checks += len(df)
        if "trip_distance" in df.columns:
            violations += (df["trip_distance"] < 0).sum()
            total_checks += len(df)
        if total_checks == 0:
            return 100.0
        validity_rate = 1 - (violations / total_checks)
        return max(0.0, validity_rate * 100)
