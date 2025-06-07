"""Tests for core fraud detection system."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

from fraud_detection.core import FraudDetectionSystem
from fraud_detection.models import Transaction, RiskLevel, Location, UserProfile
from fraud_detection.storage import RedisStorage


class TestFraudDetectionSystem:
    """Test fraud detection system."""
    
    @pytest.fixture
    def mock_storage(self):
        """Mock storage instance."""
        storage = Mock(spec=RedisStorage)
        storage.get_user_profile.return_value = None
        storage.increment_velocity_counter.return_value = 1
        storage.get_merchant_risk_score.return_value = 0.1
        storage.store_transaction.return_value = None
        storage.update_user_profile.return_value = None
        return storage
    
    @pytest.fixture
    def mock_ml_model(self):
        """Create a real simple ML model for testing."""
        model = IsolationForest(contamination=0.1, random_state=42)
        # Train on dummy data
        X_dummy = np.random.randn(100, 7)
        model.fit(X_dummy)
        return model
    
    @pytest.fixture
    def detector(self, mock_storage, mock_ml_model, tmp_path):
        """Create fraud detector with mocks."""
        # Save model to temp file
        model_path = tmp_path / "test_model.pkl"
        joblib.dump(mock_ml_model, model_path)
        
        detector = FraudDetectionSystem(
            redis_host="localhost",
            model_path=str(model_path)
        )
        detector.storage = mock_storage
        return detector
    
    def test_process_normal_transaction(self, detector, mock_storage):
        """Test processing normal transaction."""
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=50.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        # Mock user profile for existing user
        mock_profile = UserProfile(
            user_id="USER001",
            average_amount=100.0,
            transaction_count=50,
            fraud_count=0
        )
        mock_storage.get_user_profile.return_value = mock_profile
        mock_storage.increment_velocity_counter.return_value = 2
        mock_storage.get_merchant_risk_score.return_value = 0.1
        
        result = detector.process_transaction(transaction)
        
        assert result.transaction_id == "TXN123"
        assert result.is_fraud is False
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        assert 0 <= result.risk_score <= 1
        assert result.processing_time_ms > 0
        
        # Verify storage calls
        mock_storage.store_transaction.assert_called_once()
        mock_storage.update_user_profile.assert_called_once()
    
    def test_process_high_amount_transaction(self, detector, mock_storage):
        """Test processing high-amount transaction."""
        transaction = Transaction(
            transaction_id="TXN456",
            user_id="USER002",
            amount=15000.0,  # High amount
            merchant_id="MERCH999",
            timestamp=datetime.now()
        )
        
        # Mock user with history
        mock_profile = UserProfile(
            user_id="USER002",
            average_amount=100.0,
            transaction_count=10,
            fraud_count=0
        )
        mock_storage.get_user_profile.return_value = mock_profile
        
        result = detector.process_transaction(transaction)
        
        assert "HIGH_AMOUNT" in result.flags
        assert result.risk_score > 0.5  # Should be elevated
    
    def test_process_high_velocity_transaction(self, detector, mock_storage):
        """Test processing with high velocity."""
        transaction = Transaction(
            transaction_id="TXN789",
            user_id="USER003",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        # Mock high velocity
        mock_storage.increment_velocity_counter.return_value = 10
        
        result = detector.process_transaction(transaction)
        
        assert "HIGH_VELOCITY" in result.flags
    
    def test_process_unusual_time_transaction(self, detector, mock_storage):
        """Test processing transaction at unusual time."""
        # Create transaction at 3 AM
        timestamp = datetime.now().replace(hour=3, minute=0, second=0)
        transaction = Transaction(
            transaction_id="TXN999",
            user_id="USER004",
            amount=200.0,
            merchant_id="MERCH001",
            timestamp=timestamp
        )
        
        result = detector.process_transaction(transaction)
        
        assert "UNUSUAL_TIME" in result.flags
    
    def test_process_location_anomaly(self, detector, mock_storage):
        """Test processing with location anomaly."""
        # Previous location: New York
        ny_location = Location(
            latitude=40.7128,
            longitude=-74.0060,
            city="New York",
            country="USA"
        )
        
        # Current location: Los Angeles (far away)
        la_location = Location(
            latitude=34.0522,
            longitude=-118.2437,
            city="Los Angeles",
            country="USA"
        )
        
        # Mock user profile with location history
        mock_profile = UserProfile(
            user_id="USER005",
            average_amount=100.0,
            transaction_count=50,
            fraud_count=0,
            locations=[ny_location],
            last_transaction=datetime.now() - timedelta(hours=1)
        )
        mock_storage.get_user_profile.return_value = mock_profile
        
        transaction = Transaction(
            transaction_id="TXN1000",
            user_id="USER005",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now(),
            location=la_location
        )
        
        result = detector.process_transaction(transaction)
        
        # Should flag location anomaly (impossible travel)
        assert result.risk_score > 0.5
    
    def test_process_new_user_transaction(self, detector, mock_storage):
        """Test processing transaction for new user."""
        transaction = Transaction(
            transaction_id="TXN2000",
            user_id="NEW_USER",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        # Mock no existing profile
        mock_storage.get_user_profile.return_value = None
        
        result = detector.process_transaction(transaction)
        
        # New users should have moderate risk
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        assert result.transaction_id == "TXN2000"
    
    def test_feature_extraction(self, detector, mock_storage):
        """Test feature extraction details."""
        transaction = Transaction(
            transaction_id="TXN3000",
            user_id="USER006",
            amount=200.0,
            merchant_id="MERCH001",
            timestamp=datetime(2024, 1, 15, 3, 30, 0)  # 3:30 AM
        )
        
        mock_profile = UserProfile(
            user_id="USER006",
            average_amount=150.0,
            transaction_count=20,
            fraud_count=0
        )
        mock_storage.get_user_profile.return_value = mock_profile
        
        features = detector._extract_features(transaction)
        
        assert features['amount'] == 200.0
        assert features['hour_of_day'] == 3
        assert features['is_night'] is True
        assert features['amount_deviation'] == 50.0
        assert features['user_transaction_count'] == 20
    
    def test_ml_scoring(self, detector):
        """Test ML scoring functionality."""
        features = {
            'amount': 1000.0,
            'hour_of_day': 14,
            'day_of_week': 2,
            'merchant_risk_score': 0.3,
            'amount_deviation': 500.0,
            'time_since_last': 2.0,
            'location_risk': 0.1
        }
        
        score = detector._ml_scoring(features)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    def test_calculate_final_score(self, detector):
        """Test final score calculation."""
        rule_flags = ['HIGH_AMOUNT', 'VELOCITY']
        ml_score = 0.7
        
        final_score, is_fraud = detector._calculate_final_score(rule_flags, ml_score)
        
        assert 0 <= final_score <= 1
        assert isinstance(is_fraud, bool)
        # With high ML score and multiple flags, should be fraud
        assert is_fraud is True
    
    def test_error_handling(self, detector, mock_storage):
        """Test error handling in transaction processing."""
        # Make storage raise an error
        mock_storage.store_transaction.side_effect = Exception("Storage error")
        
        transaction = Transaction(
            transaction_id="TXN_ERROR",
            user_id="USER_ERROR",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        # Should raise the exception (or handle it based on implementation)
        with pytest.raises(Exception):
            detector.process_transaction(transaction)


