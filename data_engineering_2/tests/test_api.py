"""
Integration tests for the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@patch('src.main.get_session')
class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_health_endpoint_success(self, mock_get_session, client):
        """Test health endpoint when database is connected."""
        mock_session = Mock()
        mock_session.query().count.return_value = 100
        mock_get_session.return_value = mock_session
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["total_events"] == 100
    
    def test_health_endpoint_failure(self, mock_get_session, client):
        """Test health endpoint when database is down."""
        mock_get_session.side_effect = Exception("Database connection failed")
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
    
    def test_get_stats(self, mock_get_session, client):
        """Test stats endpoint."""
        mock_session = Mock()
        mock_session.query().count.return_value = 500
        mock_session.query().distinct().count.return_value = 5
        mock_session.query().scalar.return_value = datetime.utcnow()
        mock_get_session.return_value = mock_session
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_events"] == 500
        assert data["database_connected"] is True
    
    def test_get_analytics_no_data(self, mock_get_session, client):
        """Test analytics endpoint with no data."""
        mock_session = Mock()
        mock_session.query().filter().all.return_value = []
        mock_get_session.return_value = mock_session
        
        response = client.get("/api/analytics")
        
        assert response.status_code == 404
    
    def test_get_analytics_with_data(self, mock_get_session, client):
        """Test analytics endpoint with sample data."""
        # Create mock events
        mock_event1 = Mock()
        mock_event1.distance_km = 10.0
        mock_event1.cost = 15.0
        mock_event1.duration_minutes = 30.0
        mock_event1.vehicle_type = "bike"
        mock_event1.city = "Warsaw"
        
        mock_event2 = Mock()
        mock_event2.distance_km = 5.0
        mock_event2.cost = 8.0
        mock_event2.duration_minutes = 15.0
        mock_event2.vehicle_type = "scooter"
        mock_event2.city = "Krakow"
        
        mock_session = Mock()
        mock_session.query().filter().all.return_value = [mock_event1, mock_event2]
        mock_get_session.return_value = mock_session
        
        response = client.get("/api/analytics?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_trips"] == 2
        assert data["total_distance_km"] == 15.0
        assert data["total_revenue"] == 23.0
        assert "breakdown_by_vehicle" in data
        assert "breakdown_by_city" in data
    
    def test_get_recent_trips(self, mock_get_session, client):
        """Test recent trips endpoint."""
        mock_event = Mock()
        mock_event.trip_id = "TRIP-001"
        mock_event.city = "Warsaw"
        mock_event.vehicle_type = "bike"
        mock_event.distance_km = 5.0
        mock_event.duration_minutes = 15.0
        mock_event.cost = 10.0
        mock_event.timestamp = datetime.utcnow()
        
        mock_session = Mock()
        mock_session.query().order_by().limit().all.return_value = [mock_event]
        mock_get_session.return_value = mock_session
        
        response = client.get("/api/recent-trips?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["trip_id"] == "TRIP-001"
        assert data[0]["city"] == "Warsaw"
    
    def test_get_analytics_with_filters(self, mock_get_session, client):
        """Test analytics with city and vehicle type filters."""
        mock_session = Mock()
        mock_session.query().filter().filter().filter().all.return_value = []
        mock_get_session.return_value = mock_session
        
        response = client.get("/api/analytics?city=Warsaw&vehicle_type=bike")
        
        assert response.status_code == 404  # No data
