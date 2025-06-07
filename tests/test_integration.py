"""Integration tests for fraud detection system."""

import pytest
import asyncio
from datetime import datetime
import tempfile
import joblib
from sklearn.ensemble import IsolationForest
import numpy as np

from fraud_detection import FraudDetectionSystem
from fraud_detection.models import Transaction, Location
from fraud_detection.storage import RedisStorage


@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring real services."""
    
    @pytest.fixture
    def temp_model(self):
        """Create temporary model file."""
        model = IsolationForest(contamination=0.1, random_state=42)
        X_dummy = np.random.randn(100, 7)
        model.fit(X_dummy)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            joblib.dump(model, f.name)
            yield f.name
    
    @pytest.fixture
    def detector(self, temp_model):
        """Create real detector instance."""
        # Skip if Redis not available
        pytest.importorskip("redis")
        
        try:
            # Try to connect to Redis
            storage = RedisStorage(host="localhost")
            storage.client.ping()
        except Exception:
            pytest.skip("Redis not available")
        
        return FraudDetectionSystem(
            redis_host="localhost",
            model_path=temp_model
        )
    
    def test_end_to_end_processing(self, detector):
        """Test end-to-end transaction processing."""
        transaction = Transaction(
            transaction_id=f"TEST_{datetime.now().timestamp()}",
            user_id="TEST_USER",
            amount=100.0,
            merchant_id="TEST_MERCHANT",
            timestamp=datetime.now()
        )
        
        result = detector.process_transaction(transaction)
        
        assert result is not None
        assert result.transaction_id == transaction.transaction_id
        assert hasattr(result, 'risk_score')
        assert hasattr(result, 'is_fraud')
        assert result.processing_time_ms > 0
        assert 0 <= result.risk_score <= 1
    
    def test_multiple_transactions_same_user(self, detector):
        """Test processing multiple transactions for same user."""
        user_id = f"TEST_USER_{datetime.now().timestamp()}"
        
        # Process normal transactions
        for i in range(5):
            transaction = Transaction(
                transaction_id=f"TEST_{user_id}_{i}",
                user_id=user_id,
                amount=100.0 + i * 10,
                merchant_id="TEST_MERCHANT",
                timestamp=datetime.now()
            )
            
            result = detector.process_transaction(transaction)
            assert result.is_fraud is False
        
        # Process suspicious transaction (high amount)
        suspicious_transaction = Transaction(
            transaction_id=f"TEST_{user_id}_SUSPICIOUS",
            user_id=user_id,
            amount=10000.0,  # Very high amount
            merchant_id="TEST_MERCHANT",
            timestamp=datetime.now()
        )
        
        result = detector.process_transaction(suspicious_transaction)
        
        # Should be flagged due to deviation from normal pattern
        assert "HIGH_AMOUNT" in result.flags or "AMOUNT_DEVIATION" in result.flags
        assert result.risk_score > 0.5
    
    def test_location_based_detection(self, detector):
        """Test location-based fraud detection."""
        user_id = f"TEST_USER_LOC_{datetime.now().timestamp()}"
        
        # First transaction in New York
        ny_transaction = Transaction(
            transaction_id=f"TEST_{user_id}_NY",
            user_id=user_id,
            amount=100.0,
            merchant_id="TEST_MERCHANT_NY",
            timestamp=datetime.now(),
            location=Location(
                latitude=40.7128,
                longitude=-74.0060,
                city="New York",
                country="USA"
            )
        )
        
        result1 = detector.process_transaction(ny_transaction)
        assert result1.is_fraud is False
        
        # Second transaction in LA shortly after (impossible travel)
        la_transaction = Transaction(
            transaction_id=f"TEST_{user_id}_LA",
            user_id=user_id,
            amount=100.0,
            merchant_id="TEST_MERCHANT_LA",
            timestamp=datetime.now(),
            location=Location(
                latitude=34.0522,
                longitude=-118.2437,
                city="Los Angeles",
                country="USA"
            )
        )
        
        result2 = detector.process_transaction(la_transaction)
        
        # Should detect location anomaly
        assert result2.risk_score > result1.risk_score
    
    def test_velocity_checking(self, detector):
        """Test transaction velocity checking."""
        user_id = f"TEST_USER_VEL_{datetime.now().timestamp()}"
        
        # Rapid transactions
        results = []
        for i in range(10):
            transaction = Transaction(
                transaction_id=f"TEST_{user_id}_VEL_{i}",
                user_id=user_id,
                amount=50.0,
                merchant_id=f"MERCHANT_{i}",
                timestamp=datetime.now()
            )
            
            result = detector.process_transaction(transaction)
            results.append(result)
        
        # Later transactions should have velocity flags
        high_velocity_results = [r for r in results if "HIGH_VELOCITY" in r.flags]
        assert len(high_velocity_results) > 0
        
        # Risk scores should increase with velocity
        later_scores = [r.risk_score for r in results[-3:]]
        earlier_scores = [r.risk_score for r in results[:3]]
        assert max(later_scores) > max(earlier_scores)


