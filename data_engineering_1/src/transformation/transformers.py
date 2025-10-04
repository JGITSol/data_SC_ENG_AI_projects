"""
Data transformation module for cleaning and enriching trip data.
"""

from typing import Optional
import pandas as pd
from datetime import datetime

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class TripDataTransformer:
    """
    Transform raw trip data with cleaning, enrichment, and feature engineering.
    Implements:
    - Data cleaning and standardization
    - Feature engineering
    - Data enrichment
    - Type conversions
    """
    def __init__(self) -> None:
        logger.info("Initialized TripDataTransformer")
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Starting transformation of {len(df)} records")
        df_transformed = df.copy()
        df_transformed = self._standardize_column_names(df_transformed)
        df_transformed = self._convert_data_types(df_transformed)
        df_transformed = self._clean_data(df_transformed)
        df_transformed = self._engineer_features(df_transformed)
        df_transformed = self._add_metadata(df_transformed)
        logger.info(
            f"Transformation completed",
            extra={
                "input_records": len(df),
                "output_records": len(df_transformed),
                "columns": list(df_transformed.columns),
            },
        )
        return df_transformed
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        logger.debug("Standardized column names")
        return df
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        datetime_cols = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        numeric_cols = [
            "passenger_count", "trip_distance", "fare_amount",
            "extra", "mta_tax", "tip_amount", "tolls_amount",
            "improvement_surcharge", "total_amount", "congestion_surcharge"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        int_cols = ["pulocationid", "dolocationid", "passenger_count"]
        for col in int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        logger.debug("Converted data types")
        return df
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(df)
        if "tpep_pickup_datetime" in df.columns:
            df = df[df["tpep_pickup_datetime"].notna()]
        if "tpep_dropoff_datetime" in df.columns:
            df = df[df["tpep_dropoff_datetime"].notna()]
        amount_cols = ["fare_amount", "total_amount", "trip_distance"]
        for col in amount_cols:
            if col in df.columns:
                df = df[df[col] >= 0]
        if "fare_amount" in df.columns:
            df = df[df["fare_amount"] <= 1000]
        if "trip_distance" in df.columns:
            df = df[df["trip_distance"] <= 200]
        if "passenger_count" in df.columns:
            df = df[(df["passenger_count"] >= 0) & (df["passenger_count"] <= 9)]
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"Cleaned data: removed {removed_count} invalid records")
        return df
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if "tpep_pickup_datetime" in df.columns and "tpep_dropoff_datetime" in df.columns:
            df["trip_duration_minutes"] = (
                (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"])
                .dt.total_seconds() / 60
            )
        if "trip_distance" in df.columns and "trip_duration_minutes" in df.columns:
            df["average_speed_mph"] = (
                df["trip_distance"] / (df["trip_duration_minutes"] / 60)
            ).replace([float("inf"), -float("inf")], pd.NA)
        if "tpep_pickup_datetime" in df.columns:
            df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
            df["pickup_day_of_week"] = df["tpep_pickup_datetime"].dt.dayofweek
            df["pickup_day_name"] = df["tpep_pickup_datetime"].dt.day_name()
            df["is_weekend"] = df["pickup_day_of_week"].isin([5, 6])
        if "tip_amount" in df.columns and "fare_amount" in df.columns:
            df["tip_percentage"] = (
                (df["tip_amount"] / df["fare_amount"] * 100)
                .replace([float("inf"), -float("inf")], 0)
            )
        logger.debug("Engineered features")
        return df
    def _add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        df["processed_at"] = datetime.now()
        df["data_version"] = "1.0"
        return df
