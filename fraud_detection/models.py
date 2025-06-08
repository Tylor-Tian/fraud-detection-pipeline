"""Data models for fraud detection system."""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


class RiskLevel(str, Enum):
    """Risk level enumeration."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Location(BaseModel):
    """Location model."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    country: Optional[str] = None
    city: Optional[str] = None


class Transaction(BaseModel):
    """Transaction input model."""

    transaction_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    merchant_id: str = Field(..., min_length=1)
    timestamp: datetime
    location: Optional[Location] = None
    device_id: Optional[str] = None
    card_number_hash: Optional[str] = None

    @validator("timestamp")
    def timestamp_not_future(cls, v: datetime) -> datetime:
        if v > datetime.now():
            raise ValueError("Transaction timestamp cannot be in the future")
        return v


class RiskScore(BaseModel):
    """Risk score output model."""

    transaction_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    is_fraud: bool
    flags: List[str] = []
    ml_score: float = Field(..., ge=0, le=1)
    rule_score: float = Field(..., ge=0, le=1)
    explanation: Dict[str, float] = {}
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    """User risk profile model."""

    user_id: str
    transaction_count: int = 0
    average_amount: float = 0.0
    total_amount: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    last_transaction: Optional[datetime] = None
    locations: List[Location] = []
    fraud_count: int = 0
