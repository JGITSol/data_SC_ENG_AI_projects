"""
Unit tests for data validation module.
"""
import pandas as pd
import pytest
from datetime import datetime, timedelta
from src.ingestion.validators import DataValidator, ValidationResult

@pytest.fixture
def valid_trip_data() -> pd.DataFrame:
    now = datetime.now()
    return pd.DataFrame({
        "VendorID": ["1", "2"],
        "tpep_pickup_datetime": [now - timedelta(hours=1), now - timedelta(hours=2)],
        "tpep_dropoff_datetime": [now, now - timedelta(hours=1)],
        "passenger_count": [1.0, 2.0],
        "trip_distance": [2.5, 5.0],
        "fare_amount": [10.0, 20.0],
        "total_amount": [12.0, 24.0],
    })

@pytest.fixture
def invalid_trip_data() -> pd.DataFrame:
    now = datetime.now()
    return pd.DataFrame({
        "VendorID": ["1", "2"],
        "tpep_pickup_datetime": [now, now - timedelta(hours=1)],
        "tpep_dropoff_datetime": [now - timedelta(hours=1), now],
        "passenger_count": [1.0, -1.0],
        "trip_distance": [2.5, -5.0],
        "fare_amount": [-10.0, 20.0],
        "total_amount": [12.0, 24.0],
    })

class TestDataValidator:
    def test_validator_initialization(self):
        validator = DataValidator(strict_mode=False)
        assert validator is not None
        assert validator.strict_mode is False

    def test_validate_valid_data(self, valid_trip_data):
        validator = DataValidator(strict_mode=False)
        result = validator.validate(valid_trip_data)
        assert isinstance(result, ValidationResult)
        assert result.total_records == 2
        assert result.data_quality_score >= 90.0

    def test_validate_invalid_data(self, invalid_trip_data):
        validator = DataValidator(strict_mode=False)
        result = validator.validate(invalid_trip_data)
        assert isinstance(result, ValidationResult)
        assert result.invalid_records > 0
        assert len(result.validation_errors) > 0

    def test_strict_mode(self, invalid_trip_data):
        validator = DataValidator(strict_mode=True)
        result = validator.validate(invalid_trip_data)
        assert result.is_valid is False

    def test_business_rules(self, valid_trip_data):
        validator = DataValidator(strict_mode=False)
        data = valid_trip_data.copy()
        data.loc[0, "fare_amount"] = -10.0
        result = validator.validate(data)
        assert any(
            error["type"] == "business_rule"
            for error in result.validation_errors
        )
