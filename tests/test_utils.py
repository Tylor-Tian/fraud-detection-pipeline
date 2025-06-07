"""Tests for utility functions."""

import pytest
from datetime import datetime

from fraud_detection.utils import (
    calculate_distance,
    calculate_velocity,
    normalize_amount,
    get_time_features,
    generate_transaction_hash
)


class TestUtils:
    """Test utility functions."""
    
    def test_calculate_distance(self):
        """Test distance calculation between locations."""
        # New York to Los Angeles
        loc1 = {'latitude': 40.7128, 'longitude': -74.0060}
        loc2 = {'latitude': 34.0522, 'longitude': -118.2437}
        
        distance = calculate_distance(loc1, loc2)
        
        # Approximate distance should be around 3944 km
        assert 3900 < distance < 4000
    
    def test_calculate_distance_same_location(self):
        """Test distance for same location."""
        loc = {'latitude': 40.7128, 'longitude': -74.0060}
        distance = calculate_distance(loc, loc)
        assert distance == pytest.approx(0, abs=0.1)
    
    def test_calculate_velocity(self):
        """Test velocity calculation."""
        distance = 500  # km
        time = 2  # hours
        
        velocity = calculate_velocity(distance, time)
        assert velocity == 250  # km/h
    
    def test_calculate_velocity_zero_time(self):
        """Test velocity with zero time."""
        velocity = calculate_velocity(100, 0)
        assert velocity == float('inf')
    
    def test_normalize_amount(self):
        """Test amount normalization."""
        amount = 150
        mean = 100
        std = 25
        
        normalized = normalize_amount(amount, mean, std)
        assert normalized == 2.0
    
    def test_normalize_amount_zero_std(self):
        """Test normalization with zero standard deviation."""
        normalized = normalize_amount(100, 100, 0)
        assert normalized == 0
    
    def test_get_time_features(self):
        """Test time feature extraction."""
        # Monday at 3 PM
        timestamp = datetime(2024, 1, 15, 15, 30, 0)
        features = get_time_features(timestamp)
        
        assert features['hour'] == 15
        assert features['day_of_week'] == 0  # Monday
        assert features['day_of_month'] == 15
        assert features['is_weekend'] is False
        assert features['is_night'] is False
        
        # Saturday at 2 AM
        timestamp = datetime(2024, 1, 20, 2, 0, 0)
        features = get_time_features(timestamp)
        
        assert features['is_weekend'] is True
        assert features['is_night'] is True
        assert features['hour'] == 2
        assert features['day_of_week'] == 5  # Saturday
    
    def test_generate_transaction_hash(self):
        """Test transaction hash generation."""
        transaction1 = {
            "transaction_id": "TXN123",
            "amount": 100.0,
            "user_id": "USER001"
        }
        
        transaction2 = {
            "transaction_id": "TXN123",
            "amount": 100.0,
            "user_id": "USER001"
        }
        
        transaction3 = {
            "transaction_id": "TXN124",
            "amount": 100.0,
            "user_id": "USER001"
        }
        
        # Same transaction should produce same hash
        hash1 = generate_transaction_hash(transaction1)
        hash2 = generate_transaction_hash(transaction2)
        assert hash1 == hash2
        
        # Different transaction should produce different hash
        hash3 = generate_transaction_hash(transaction3)
        assert hash1 != hash3


