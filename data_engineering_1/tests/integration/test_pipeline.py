"""
Integration test for the full NYC Taxi pipeline (ingestion, validation, transformation).
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.ingestion.extractors import TaxiDataExtractor, ZoneDataExtractor
from src.ingestion.validators import DataValidator
from src.transformation.transformers import TripDataTransformer
from src.utils.data_quality import DataQualityMonitor

def test_full_pipeline(tmp_path):
    # Extract raw taxi trips
    # Mockowanie pobierania danych, aby test nie zależał od zewnętrznego URL
    import pandas as pd
    from unittest.mock import patch
    sample_data = pd.DataFrame({
        'VendorID': ['1', '2'],
        'tpep_pickup_datetime': ['2025-10-07 17:17:03', '2025-10-07 18:17:03'],
        'tpep_dropoff_datetime': ['2025-10-07 18:17:03', '2025-10-07 19:17:03'],
        'passenger_count': [1.0, 2.0],
        'trip_distance': [2.5, 5.0],
        'pickup_longitude': [40.7128, 40.7138],
        'pickup_latitude': [-74.0060, -74.0050],
        'RatecodeID': ['1', '2'],
        'store_and_fwd_flag': ['N', 'Y'],
        'PULocationID': [100, 101],
        'DOLocationID': [200, 201],
        'payment_type': ['Credit', 'Cash'],
        'fare_amount': [10.0, 20.0],
        'extra': [1.0, 2.0],
        'mta_tax': [0.5, 0.5],
        'tip_amount': [2.0, 4.0],
        'tolls_amount': [0.0, 0.0],
        'improvement_surcharge': [0.3, 0.3],
        'total_amount': [12.0, 24.0],
        'congestion_surcharge': [2.5, 2.5],
        'vendor_id': ['1', '2'],
        'dropoff_location_id': [200, 201],
        'rate_code_id': ['1', '2'],
        'pickup_location_id': [100, 101]
    })
    with patch('src.ingestion.extractors.pd.read_csv', return_value=sample_data):
        taxi_extractor = TaxiDataExtractor(output_dir=tmp_path)
        df_raw = taxi_extractor.extract(max_records=2)
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
