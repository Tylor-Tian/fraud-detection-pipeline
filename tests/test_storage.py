"""Tests for storage layer."""

import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime

from fraud_detection.storage import RedisStorage
from fraud_detection.models import Transaction, UserProfile, Location
from fraud_detection.exceptions import StorageError


class TestRedisStorage:
    """Test Redis storage operations."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        mock = Mock()
        mock.ping.return_value = True
        mock.get.return_value = None
        mock.set.return_value = True
        mock.setex.return_value = True
        mock.incr.return_value = 1
        mock.expire.return_value = True
        return mock
    
    @pytest.fixture
    def storage(self, mock_redis_client):
        """Create storage instance with mocked Redis."""
        with patch('fraud_detection.storage.redis.Redis') as mock_redis:
            mock_redis.return_value = mock_redis_client
            storage = RedisStorage()
            storage.client = mock_redis_client
            return storage
    
    def test_connection_error(self):
        """Test Redis connection error handling."""
        with patch('fraud_detection.storage.redis.Redis') as mock_redis:
            mock_redis.side_effect = Exception("Connection failed")
            
            with pytest.raises(StorageError) as exc_info:
                RedisStorage()
            
            assert "Redis connection failed" in str(exc_info.value)
    
    def test_store_transaction(self, storage, mock_redis_client):
        """Test storing transaction."""
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        storage.store_transaction(transaction, risk_score=0.75)
        
        # Verify Redis was called
        mock_redis_client.setex.assert_called_once()
        call_args = mock_redis_client.setex.call_args
        
        assert call_args[0][0] == "tx:TXN123"
        assert call_args[0][1] == 86400 * 7  # 7 days TTL
        
        # Verify stored data
        stored_data = json.loads(call_args[0][2])
        assert stored_data['transaction_id'] == "TXN123"
        assert stored_data['risk_score'] == 0.75
        assert 'processed_at' in stored_data
    
    def test_get_user_profile_exists(self, storage, mock_redis_client):
        """Test getting existing user profile."""
        profile_data = {
            "user_id": "USER001",
            "transaction_count": 10,
            "average_amount": 150.0,
            "total_amount": 1500.0,
            "risk_level": "LOW",
            "fraud_count": 0,
            "locations": []
        }
        
        mock_redis_client.get.return_value = json.dumps(profile_data)
        
        profile = storage.get_user_profile("USER001")
        
        assert profile is not None
        assert profile.user_id == "USER001"
        assert profile.transaction_count == 10
        assert profile.average_amount == 150.0
        mock_redis_client.get.assert_called_with("user:USER001")
    
    def test_get_user_profile_not_exists(self, storage, mock_redis_client):
        """Test getting non-existent user profile."""
        mock_redis_client.get.return_value = None
        
        profile = storage.get_user_profile("USER999")
        
        assert profile is None
    
    def test_update_user_profile_new_user(self, storage, mock_redis_client):
        """Test updating profile for new user."""
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        # Mock no existing profile
        mock_redis_client.get.return_value = None
        
        storage.update_user_profile("USER001", transaction, is_fraud=False)
        
        # Verify profile was created and stored
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        
        stored_data = json.loads(call_args[0][1])
        assert stored_data['user_id'] == "USER001"
        assert stored_data['transaction_count'] == 1
        assert stored_data['average_amount'] == 100.0
        assert stored_data['fraud_count'] == 0
    
    def test_update_user_profile_existing_user(self, storage, mock_redis_client):
        """Test updating existing user profile."""
        existing_profile = {
            "user_id": "USER001",
            "transaction_count": 10,
            "average_amount": 100.0,
            "total_amount": 1000.0,
            "risk_level": "LOW",
            "fraud_count": 1,
            "locations": []
        }
        
        mock_redis_client.get.return_value = json.dumps(existing_profile)
        
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=200.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        storage.update_user_profile("USER001", transaction, is_fraud=True)
        
        # Verify updated profile
        call_args = mock_redis_client.set.call_args
        stored_data = json.loads(call_args[0][1])
        
        assert stored_data['transaction_count'] == 11
        assert stored_data['total_amount'] == 1200.0
        assert stored_data['average_amount'] == pytest.approx(109.09, rel=0.01)
        assert stored_data['fraud_count'] == 2
    
    def test_increment_velocity_counter(self, storage, mock_redis_client):
        """Test incrementing velocity counter."""
        mock_redis_client.incr.return_value = 3
        
        count = storage.increment_velocity_counter("USER001")
        
        assert count == 3
        mock_redis_client.incr.assert_called_once()
        
        # Verify key format includes hour
        call_args = mock_redis_client.incr.call_args
        key = call_args[0][0]
        assert key.startswith("velocity:USER001:")
        
        # Verify expiry was set
        mock_redis_client.expire.assert_called_once()
        expire_args = mock_redis_client.expire.call_args
        assert expire_args[0][1] == 3600  # 1 hour
    
    def test_get_merchant_risk_score_exists(self, storage, mock_redis_client):
        """Test getting existing merchant risk score."""
        mock_redis_client.get.return_value = "0.75"
        
        score = storage.get_merchant_risk_score("MERCH001")
        
        assert score == 0.75
        mock_redis_client.get.assert_called_with("merchant:MERCH001:risk")
    
    def test_get_merchant_risk_score_not_exists(self, storage, mock_redis_client):
        """Test getting non-existent merchant risk score."""
        mock_redis_client.get.return_value = None
        
        score = storage.get_merchant_risk_score("MERCH999")
        
        assert score == 0.1  # Default score
    
    def test_storage_error_handling(self, storage, mock_redis_client):
        """Test error handling in storage operations."""
        mock_redis_client.setex.side_effect = Exception("Redis error")
        
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=100.0,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        with pytest.raises(StorageError):
            storage.store_transaction(transaction, 0.5)


