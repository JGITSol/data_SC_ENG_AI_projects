"""
Tests for Kafka producer and consumer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.kafka_producer import UrbanMobilityDataGenerator, MobilityKafkaProducer
from src.kafka_consumer import MobilityEventProcessor


class TestUrbanMobilityDataGenerator:
    """Test data generator."""
    
    def test_generate_trip_event_structure(self):
        """Test that generated events have required fields."""
        generator = UrbanMobilityDataGenerator()
        event = generator.generate_trip_event()
        
        # Check required fields
        assert "trip_id" in event
        assert "city" in event
        assert "vehicle_type" in event
        assert "start_location" in event
        assert "end_location" in event
        assert "distance_km" in event
        assert "duration_minutes" in event
        assert "cost" in event
        assert "timestamp" in event
        assert "metadata" in event
    
    def test_trip_id_increments(self):
        """Test that trip IDs increment properly."""
        generator = UrbanMobilityDataGenerator()
        event1 = generator.generate_trip_event()
        event2 = generator.generate_trip_event()
        
        assert event1["trip_id"] != event2["trip_id"]
        assert event1["trip_id"] < event2["trip_id"]
    
    def test_generated_data_ranges(self):
        """Test that generated data is within reasonable ranges."""
        generator = UrbanMobilityDataGenerator()
        event = generator.generate_trip_event()
        
        # Check ranges
        assert 0 < event["distance_km"] < 20
        assert 0 < event["duration_minutes"] < 100
        assert 0 < event["cost"] < 30
        
        # Check location coordinates (roughly Warsaw area)
        assert 51 < event["start_location"]["lat"] < 54
        assert 20 < event["start_location"]["lon"] < 22
    
    def test_vehicle_types(self):
        """Test that vehicle types are from expected set."""
        generator = UrbanMobilityDataGenerator()
        events = [generator.generate_trip_event() for _ in range(20)]
        
        valid_types = {"bike", "scooter", "bus", "tram", "metro"}
        for event in events:
            assert event["vehicle_type"] in valid_types


class TestMobilityEventProcessor:
    """Test event processor."""
    
    def test_validate_event_valid(self):
        """Test validation of valid event."""
        event = {
            "trip_id": "TRIP-001",
            "city": "Warsaw",
            "vehicle_type": "bike",
            "start_location": {"lat": 52.2297, "lon": 21.0122},
            "end_location": {"lat": 52.2397, "lon": 21.0222},
            "distance_km": 5.0,
            "duration_minutes": 15.0,
            "cost": 10.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        processor = MobilityEventProcessor()
        assert processor.validate_event(event) is True
    
    def test_validate_event_missing_field(self):
        """Test validation fails with missing field."""
        event = {
            "trip_id": "TRIP-001",
            "city": "Warsaw",
            # Missing vehicle_type
            "start_location": {"lat": 52.2297, "lon": 21.0122},
            "end_location": {"lat": 52.2397, "lon": 21.0222},
            "distance_km": 5.0,
            "duration_minutes": 15.0,
            "cost": 10.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        processor = MobilityEventProcessor()
        assert processor.validate_event(event) is False
    
    def test_validate_event_invalid_range(self):
        """Test validation fails with invalid data range."""
        event = {
            "trip_id": "TRIP-001",
            "city": "Warsaw",
            "vehicle_type": "bike",
            "start_location": {"lat": 52.2297, "lon": 21.0122},
            "end_location": {"lat": 52.2397, "lon": 21.0222},
            "distance_km": -5.0,  # Invalid negative distance
            "duration_minutes": 15.0,
            "cost": 10.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        processor = MobilityEventProcessor()
        assert processor.validate_event(event) is False
    
    def test_enrich_event(self):
        """Test event enrichment."""
        event = {
            "trip_id": "TRIP-001",
            "distance_km": 10.0,
            "duration_minutes": 30.0,
            "cost": 15.0
        }
        
        processor = MobilityEventProcessor()
        enriched = processor.enrich_event(event)
        
        # Check calculated fields
        assert "avg_speed_kmh" in enriched
        assert "cost_per_km" in enriched
        assert "processed_at" in enriched
        
        # Check calculations
        assert enriched["avg_speed_kmh"] == 20.0  # 10km / 0.5hr
        assert enriched["cost_per_km"] == 1.5  # 15 / 10


@patch('src.kafka_producer.KafkaProducer')
class TestMobilityKafkaProducer:
    """Test Kafka producer."""
    
    def test_initialization(self, mock_kafka_producer):
        """Test producer initialization."""
        producer = MobilityKafkaProducer(
            bootstrap_servers="localhost:9092",
            topic="test-topic"
        )
        
        assert producer.topic == "test-topic"
        assert producer.generator is not None
        mock_kafka_producer.assert_called_once()
    
    def test_send_event(self, mock_kafka_producer):
        """Test sending event."""
        mock_producer_instance = Mock()
        mock_future = Mock()
        mock_future.get = Mock(return_value=Mock(partition=0, offset=123))
        mock_producer_instance.send = Mock(return_value=mock_future)
        mock_kafka_producer.return_value = mock_producer_instance
        
        producer = MobilityKafkaProducer()
        event = {
            "trip_id": "TRIP-001",
            "city": "Warsaw",
            "vehicle_type": "bike"
        }
        
        producer.send_event(event)
        
        mock_producer_instance.send.assert_called_once()
        arg_topic, arg_kwargs = mock_producer_instance.send.call_args
        assert arg_topic == ("urban-mobility-events",)
        assert arg_kwargs["key"] == "Warsaw"
