"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from fraud_detection.api import app
from fraud_detection.models import RiskScore, RiskLevel


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_detector():
    """Mock fraud detector."""
    mock = Mock()
    mock.process_transaction.return_value = RiskScore(
        transaction_id="TXN123",
        risk_score=0.25,
        risk_level=RiskLevel.LOW,
        is_fraud=False,
        flags=[],
        ml_score=0.2,
        rule_score=0.3,
        processing_time_ms=45.2
    )
    return mock


class TestAPI:
    """Test API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data
    
    @patch('fraud_detection.api.detector')
    def test_process_transaction(self, mock_detector_global, client, auth_headers, mock_detector):
        """Test single transaction processing."""
        mock_detector_global.process_transaction = mock_detector.process_transaction
        
        transaction_data = {
            "transaction_id": "TXN123",
            "user_id": "USER001",
            "amount": 100.0,
            "merchant_id": "MERCH001",
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post(
            "/transactions",
            json=transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "TXN123"
        assert data["risk_score"] == 0.25
        assert data["is_fraud"] is False
    
    def test_invalid_transaction(self, client, auth_headers):
        """Test invalid transaction data."""
        invalid_data = {
            "transaction_id": "TXN123",
            "user_id": "USER001",
            "amount": -100.0,  # Invalid negative amount
            "merchant_id": "MERCH001",
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post(
            "/transactions",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_auth(self, client):
        """Test missing authentication."""
        transaction_data = {
            "transaction_id": "TXN123",
            "user_id": "USER001",
            "amount": 100.0,
            "merchant_id": "MERCH001",
            "timestamp": datetime.now().isoformat()
        }
        
        response = client.post("/transactions", json=transaction_data)
        
        assert response.status_code == 401  # Unauthorized
    
    @patch('fraud_detection.api.detector')
    def test_batch_processing(self, mock_detector_global, client, auth_headers, mock_detector):
        """Test batch transaction processing."""
        mock_detector_global.process_transaction = mock_detector.process_transaction
        
        batch_data = {
            "transactions": [
                {
                    "transaction_id": "TXN001",
                    "user_id": "USER001",
                    "amount": 100.0,
                    "merchant_id": "MERCH001",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "transaction_id": "TXN002",
                    "user_id": "USER002",
                    "amount": 200.0,
                    "merchant_id": "MERCH002",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        response = client.post(
            "/transactions/batch",
            json=batch_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["summary"]["total_processed"] == 2
    
    def test_get_user_profile(self, client, auth_headers):
        """Test getting user profile."""
        with patch('fraud_detection.api.storage') as mock_storage:
            mock_storage.get_user_profile.return_value = Mock(
                user_id="USER001",
                transaction_count=100,
                average_amount=150.0,
                risk_level=RiskLevel.LOW,
                dict=lambda: {
                    "user_id": "USER001",
                    "transaction_count": 100,
                    "average_amount": 150.0,
                    "risk_level": "LOW"
                }
            )
            
            response = client.get(
                "/users/USER001/profile",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "USER001"
            assert data["transaction_count"] == 100
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "fraud_detection_transactions_total" in response.text
        assert "fraud_detection_processing_time_seconds" in response.text


