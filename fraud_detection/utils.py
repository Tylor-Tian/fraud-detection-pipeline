"""Utility functions for fraud detection system."""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict
import numpy as np
from math import radians, sin, cos, sqrt, atan2


def generate_transaction_hash(transaction: Dict[str, Any]) -> str:
    """Generate unique hash for transaction."""
    content = json.dumps(transaction, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()


def calculate_distance(loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
    """Calculate distance between two locations in kilometers."""
    R = 6371  # Earth's radius in kilometers

    lat1, lon1 = radians(loc1["latitude"]), radians(loc1["longitude"])
    lat2, lon2 = radians(loc2["latitude"]), radians(loc2["longitude"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def calculate_velocity(distance_km: float, time_hours: float) -> float:
    """Calculate travel velocity in km/h."""
    if time_hours == 0:
        return float("inf")
    return distance_km / time_hours


def normalize_amount(amount: float, mean: float, std: float) -> float:
    """Normalize transaction amount."""
    if std == 0:
        return 0
    return (amount - mean) / std


def get_time_features(timestamp: datetime) -> Dict[str, int]:
    """Extract time-based features from timestamp."""
    return {
        "hour": timestamp.hour,
        "day_of_week": timestamp.weekday(),
        "day_of_month": timestamp.day,
        "is_weekend": timestamp.weekday() >= 5,
        "is_night": timestamp.hour < 6 or timestamp.hour > 22,
    }
