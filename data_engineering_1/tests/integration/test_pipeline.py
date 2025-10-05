"""
Integration test for the full NYC Taxi pipeline (ingestion, validation, transformation).
"""
from src.ingestion.extractors import TaxiDataExtractor, ZoneDataExtractor
from src.ingestion.validators import DataValidator
from src.transformation.transformers import TripDataTransformer
from src.utils.data_quality import DataQualityMonitor

def test_full_pipeline(tmp_path):
    # Extract raw taxi trips
    taxi_extractor = TaxiDataExtractor(output_dir=tmp_path)
    df_raw = taxi_extractor.extract(max_records=1000)
    assert not df_raw.empty
    # Validate data
    validator = DataValidator(strict_mode=False)
    validation_result = validator.validate(df_raw)
    assert validation_result.is_valid
    # Data quality metrics
    monitor = DataQualityMonitor()
    metrics = monitor.calculate_metrics(df_raw)
    assert metrics.overall_score > 80.0
    # Transform data
    transformer = TripDataTransformer()
    df_transformed = transformer.transform(df_raw)
    assert "trip_duration_minutes" in df_transformed.columns
    assert "average_speed_mph" in df_transformed.columns
    assert len(df_transformed) > 0
    # Save transformed data
    out_path = tmp_path / "trips_transformed.parquet"
    df_transformed.to_parquet(out_path, engine="pyarrow", index=False)
    assert out_path.exists()
    # Extract zone lookup
    zone_extractor = ZoneDataExtractor(output_dir=tmp_path)
    df_zones = zone_extractor.extract()
    assert not df_zones.empty
