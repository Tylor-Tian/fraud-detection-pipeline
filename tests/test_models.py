"""Tests for data models."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from fraud_detection.models import Transaction, Location, RiskScore, RiskLevel, UserProfile


class TestTransaction:
    """Test Transaction model."""
    
    def test_valid_transaction(self):
        """Test creating valid transaction."""
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=100.50,
            merchant_id="MERCH001",
            timestamp=datetime.now()
        )
        
        assert transaction.transaction_id == "TXN123"
        assert transaction.amount == 100.50
        assert transaction.user_id == "USER001"
        assert transaction.merchant_id == "MERCH001"
        
    def test_transaction_with_location(self):
        """Test transaction with location data."""
        location = Location(
            latitude=40.7128,
            longitude=-74.0060,
            country="USA",
            city="New York"
        )
        
        transaction = Transaction(
            transaction_id="TXN123",
            user_id="USER001",
            amount=100.50,
            merchant_id="MERCH001",
            timestamp=datetime.now(),
            location=location
        )
        
        assert transaction.location.city == "New York"
        assert transaction.location.latitude == 40.7128
    
    def test_invalid_amount(self):
        """Test transaction with invalid amount."""
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                transaction_id="TXN123",
                user_id="USER001",
                amount=-100,  # Negative amount
                merchant_id="MERCH001",
                timestamp=datetime.now()
            )
        
        assert "greater than 0" in str(exc_info.value)
    
    def test_future_timestamp(self):
        """Test transaction with future timestamp."""
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                transaction_id="TXN123",
                user_id="USER001",
                amount=100,
                merchant_id="MERCH001",
                timestamp=datetime.now() + timedelta(days=1)
            )
        
        assert "future" in str(exc_info.value).lower()
    
    def test_empty_transaction_id(self):
        """Test transaction with empty ID."""
        with pytest.raises(ValidationError):
            Transaction(
                transaction_id="",  # Empty ID
                user_id="USER001",
                amount=100,
                merchant_id="MERCH001",
                timestamp=datetime.now()
            )


class TestLocation:
    """Test Location model."""
    
    def test_valid_location(self):
        """Test valid location creation."""
        location = Location(
            latitude=40.7128,
            longitude=-74.0060,
            country="USA",
            city="New York"
        )
        
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060
        assert location.country == "USA"
        assert location.city == "New York"
    
    def test_invalid_latitude(self):
        """Test invalid latitude bounds."""
        with pytest.raises(ValidationError):
            Location(latitude=91, longitude=0)  # > 90
        
        with pytest.raises(ValidationError):
            Location(latitude=-91, longitude=0)  # < -90
    
    def test_invalid_longitude(self):
        """Test invalid longitude bounds."""
        with pytest.raises(ValidationError):
            Location(latitude=0, longitude=181)  # > 180
        
        with pytest.raises(ValidationError):
            Location(latitude=0, longitude=-181)  # < -180


class TestRiskScore:
    """Test RiskScore model."""
    
    def test_risk_score_creation(self):
        """Test creating risk score."""
        risk_score = RiskScore(
            transaction_id="TXN123",
            risk_score=0.85,
            risk_level=RiskLevel.HIGH,
            is_fraud=True,
            flags=["HIGH_AMOUNT", "VELOCITY"],
            ml_score=0.9,
            rule_score=0.8,
            processing_time_ms=45.2
        )
        
        assert risk_score.risk_score == 0.85
        assert risk_score.risk_level == RiskLevel.HIGH
        assert "HIGH_AMOUNT" in risk_score.flags
        assert len(risk_score.flags) == 2
        assert risk_score.is_fraud is True
    
    def test_risk_score_bounds(self):
        """Test risk score bounds validation."""
        # Test score > 1
        with pytest.raises(ValidationError):
            RiskScore(
                transaction_id="TXN123",
                risk_score=1.5,  # Out of bounds
                risk_level=RiskLevel.HIGH,
                is_fraud=True,
                ml_score=0.9,
                rule_score=0.8,
                processing_time_ms=45.2
            )
        
        # Test score < 0
        with pytest.raises(ValidationError):
            RiskScore(
                transaction_id="TXN123",
                risk_score=-0.1,  # Out of bounds
                risk_level=RiskLevel.LOW,
                is_fraud=False,
                ml_score=0.1,
                rule_score=0.1,
                processing_time_ms=45.2
            )
    
    def test_default_timestamp(self):
        """Test default timestamp is set."""
        risk_score = RiskScore(
            transaction_id="TXN123",
            risk_score=0.5,
            risk_level=RiskLevel.MEDIUM,
            is_fraud=False,
            ml_score=0.5,
            rule_score=0.5,
            processing_time_ms=30.0
        )
        
        assert risk_score.timestamp is not None
        assert isinstance(risk_score.timestamp, datetime)


class TestUserProfile:
    """Test UserProfile model."""
    
    def test_user_profile_defaults(self):
        """Test user profile with defaults."""
        profile = UserProfile(user_id="USER001")
        
        assert profile.user_id == "USER001"
        assert profile.transaction_count == 0
        assert profile.average_amount == 0.0
        assert profile.risk_level == RiskLevel.LOW
        assert profile.fraud_count == 0
        assert len(profile.locations) == 0
    
    def test_user_profile_with_data(self):
        """Test user profile with full data."""
        location = Location(latitude=40.7128, longitude=-74.0060)
        profile = UserProfile(
            user_id="USER001",
            transaction_count=100,
            average_amount=150.50,
            total_amount=15050.0,
            risk_level=RiskLevel.MEDIUM,
            last_transaction=datetime.now(),
            locations=[location],
            fraud_count=2
        )
        
        assert profile.transaction_count == 100
        assert profile.average_amount == 150.50
        assert profile.risk_level == RiskLevel.MEDIUM
        assert len(profile.locations) == 1

