"""
Dagster assets for pipeline orchestration.
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
from dagster import asset, AssetExecutionContext, AssetIn, MetadataValue, Output
from src.ingestion.extractors import TaxiDataExtractor, ZoneDataExtractor
from src.ingestion.validators import DataValidator
from src.transformation.transformers import TripDataTransformer
from src.utils.data_quality import DataQualityMonitor
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

@asset(group_name="ingestion")
def raw_taxi_trips(context: AssetExecutionContext) -> Output[pd.DataFrame]:
    logger.info("Starting raw taxi trips extraction")
    extractor = TaxiDataExtractor(output_dir=Path("data/raw"))
    df = extractor.extract(max_records=100000)
    filepath = extractor.save(df)
    metadata = {
        "num_records": len(df),
        "num_columns": len(df.columns),
        "file_size_mb": round(filepath.stat().st_size / (1024 * 1024), 2),
        "filepath": str(filepath),
        "preview": MetadataValue.md(df.head(10).to_markdown()),
    }
    context.log.info(f"Extracted {len(df)} raw trip records")
    return Output(df, metadata=metadata)

@asset(group_name="ingestion")
def raw_zone_lookup(context: AssetExecutionContext) -> Output[pd.DataFrame]:
    logger.info("Starting zone lookup extraction")
    extractor = ZoneDataExtractor(output_dir=Path("data/raw"))
    df = extractor.extract()
    filepath = extractor.save(df)
    metadata = {
        "num_zones": len(df),
        "boroughs": df["Borough"].nunique() if "Borough" in df.columns else 0,
        "filepath": str(filepath),
    }
    context.log.info(f"Extracted {len(df)} zone records")
    return Output(df, metadata=metadata)

@asset(ins={"raw_taxi_trips": AssetIn()}, group_name="validation")
def validated_taxi_trips(context: AssetExecutionContext, raw_taxi_trips: pd.DataFrame) -> Output[pd.DataFrame]:
    logger.info("Starting data validation")
    validator = DataValidator(strict_mode=False)
    validation_result = validator.validate(raw_taxi_trips)
    monitor = DataQualityMonitor()
    quality_metrics = monitor.calculate_metrics(raw_taxi_trips)
    metadata = {
        "is_valid": validation_result.is_valid,
        "quality_score": validation_result.data_quality_score,
        "valid_records": validation_result.valid_records,
        "invalid_records": validation_result.invalid_records,
        "num_errors": len(validation_result.validation_errors),
        "num_warnings": len(validation_result.warnings),
        "completeness_score": quality_metrics.completeness_score,
        "overall_quality": quality_metrics.overall_score,
    }
    context.log.info(f"Validation completed with quality score: {validation_result.data_quality_score}")
    return Output(raw_taxi_trips, metadata=metadata)

@asset(ins={"validated_taxi_trips": AssetIn()}, group_name="transformation")
def transformed_taxi_trips(context: AssetExecutionContext, validated_taxi_trips: pd.DataFrame) -> Output[pd.DataFrame]:
    logger.info("Starting data transformation")
    transformer = TripDataTransformer()
    df_transformed = transformer.transform(validated_taxi_trips)
    output_path = Path("data/processed/trips_transformed.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_transformed.to_parquet(output_path, engine="pyarrow", index=False)
    metadata = {
        "num_records": len(df_transformed),
        "num_columns": len(df_transformed.columns),
        "new_features": [
            "trip_duration_minutes", "average_speed_mph",
            "pickup_hour", "is_weekend", "tip_percentage"
        ],
        "filepath": str(output_path),
    }
    context.log.info(f"Transformation completed: {len(df_transformed)} records")
    return Output(df_transformed, metadata=metadata)
