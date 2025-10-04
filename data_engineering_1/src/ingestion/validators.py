"""
Data validation module with comprehensive schema and quality checks.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any

import pandas as pd
from pydantic import BaseModel, Field, validator

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class TripRecordSchema(BaseModel):
    """Expected schema for taxi trip records."""
    vendor_id: Optional[str] = Field(None, alias="VendorID")
    tpep_pickup_datetime: str
    tpep_dropoff_datetime: str
    passenger_count: Optional[float]
    trip_distance: Optional[float]
    pickup_longitude: Optional[float] = Field(None, alias="pickup_longitude")
    pickup_latitude: Optional[float] = Field(None, alias="pickup_latitude")
    rate_code_id: Optional[str] = Field(None, alias="RatecodeID")
    store_and_fwd_flag: Optional[str]
    pickup_location_id: Optional[int] = Field(None, alias="PULocationID")
    dropoff_location_id: Optional[int] = Field(None, alias="DOLocationID")
    payment_type: Optional[str]
    fare_amount: Optional[float]
    extra: Optional[float]
    mta_tax: Optional[float]
    tip_amount: Optional[float]
    tolls_amount: Optional[float]
    improvement_surcharge: Optional[float]
    total_amount: Optional[float]
    congestion_surcharge: Optional[float]
    class Config:
        allow_population_by_field_name = True
        extra = "allow"

@dataclass
class ValidationResult:
    """Results from data validation."""
    is_valid: bool
    total_records: int
    valid_records: int
    invalid_records: int
    validation_errors: List[Dict[str, Any]]
    warnings: List[str]
    data_quality_score: float

class DataValidator:
    """
    Comprehensive data validation with business rules and quality checks.
    Implements multiple validation layers:
    - Schema validation
    - Data type validation
    - Business logic validation
    - Statistical anomaly detection
    """
    def __init__(self, strict_mode: bool = False) -> None:
        self.strict_mode = strict_mode
        logger.info(f"Initialized DataValidator (strict_mode={strict_mode})")
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        logger.info(f"Starting validation of {len(df)} records")
        validation_errors: List[Dict[str, Any]] = []
        warnings: List[str] = []
        schema_errors = self._validate_schema(df)
        validation_errors.extend(schema_errors)
        required_errors = self._validate_required_columns(df)
        validation_errors.extend(required_errors)
        type_errors = self._validate_data_types(df)
        validation_errors.extend(type_errors)
        business_errors, business_warnings = self._validate_business_rules(df)
        validation_errors.extend(business_errors)
        warnings.extend(business_warnings)
        stat_warnings = self._validate_statistical_anomalies(df)
        warnings.extend(stat_warnings)
        invalid_records = len(validation_errors)
        valid_records = len(df) - invalid_records
        data_quality_score = (valid_records / len(df) * 100) if len(df) > 0 else 0.0
        is_valid = invalid_records == 0 if self.strict_mode else data_quality_score >= 90.0
        result = ValidationResult(
            is_valid=is_valid,
            total_records=len(df),
            valid_records=valid_records,
            invalid_records=invalid_records,
            validation_errors=validation_errors,
            warnings=warnings,
            data_quality_score=round(data_quality_score, 2),
        )
        logger.info(
            "Validation completed",
            extra={
                "is_valid": result.is_valid,
                "quality_score": result.data_quality_score,
                "errors": len(validation_errors),
                "warnings": len(warnings),
            },
        )
        return result
    def _validate_schema(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        errors = []
        expected_cols = set(TripRecordSchema.__fields__.keys())
        actual_cols = set(df.columns.str.lower())
        missing_cols = expected_cols - actual_cols
        if missing_cols:
            errors.append({
                "type": "schema_error",
                "message": f"Missing expected columns: {missing_cols}",
            })
        return errors
    def _validate_required_columns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        errors = []
        required_cols = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
        for col in required_cols:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    errors.append({
                        "type": "null_value",
                        "column": col,
                        "null_count": int(null_count),
                        "message": f"Required column '{col}' has {null_count} null values",
                    })
        return errors
    def _validate_data_types(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        errors = []
        numeric_cols = ["fare_amount", "total_amount", "trip_distance", "passenger_count"]
        for col in numeric_cols:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors="coerce")
                except Exception as e:
                    errors.append({
                        "type": "type_error",
                        "column": col,
                        "message": f"Column '{col}' contains invalid numeric values: {e}",
                    })
        return errors
    def _validate_business_rules(self, df: pd.DataFrame) -> tuple[List[Dict[str, Any]], List[str]]:
        errors = []
        warnings = []
        if "fare_amount" in df.columns:
            negative_fares = (df["fare_amount"] < 0).sum()
            if negative_fares > 0:
                errors.append({
                    "type": "business_rule",
                    "rule": "positive_fare",
                    "violations": int(negative_fares),
                    "message": f"{negative_fares} records have negative fare amounts",
                })
        if "trip_distance" in df.columns:
            zero_distance = (df["trip_distance"] <= 0).sum()
            if zero_distance > len(df) * 0.05:
                warnings.append(f"{zero_distance} records have zero or negative trip distance")
        if "tpep_pickup_datetime" in df.columns and "tpep_dropoff_datetime" in df.columns:
            try:
                pickup = pd.to_datetime(df["tpep_pickup_datetime"])
                dropoff = pd.to_datetime(df["tpep_dropoff_datetime"])
                invalid_times = (dropoff <= pickup).sum()
                if invalid_times > 0:
                    errors.append({
                        "type": "business_rule",
                        "rule": "chronological_times",
                        "violations": int(invalid_times),
                        "message": f"{invalid_times} records have dropoff before pickup",
                    })
            except Exception:
                pass
        if "passenger_count" in df.columns:
            high_passenger = (df["passenger_count"] > 6).sum()
            if high_passenger > 0:
                warnings.append(f"{high_passenger} records have more than 6 passengers")
        return errors, warnings
    def _validate_statistical_anomalies(self, df: pd.DataFrame) -> List[str]:
        warnings = []
        if "fare_amount" in df.columns:
            Q1 = df["fare_amount"].quantile(0.25)
            Q3 = df["fare_amount"].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df["fare_amount"] < (Q1 - 3 * IQR)) | 
                       (df["fare_amount"] > (Q3 + 3 * IQR))).sum()
            if outliers > len(df) * 0.01:
                warnings.append(f"{outliers} fare amount outliers detected")
        if "trip_distance" in df.columns:
            mean_distance = df["trip_distance"].mean()
            if mean_distance > 100:
                warnings.append(f"Average trip distance is unusually high: {mean_distance:.2f} miles")
        return warnings
