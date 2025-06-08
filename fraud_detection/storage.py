"""Storage layer for fraud detection system."""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redis
from loguru import logger

from .models import Transaction, UserProfile
from .exceptions import StorageError


class RedisStorage:
    """Redis storage implementation."""

    def __init__(
        self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None
    ) -> None:
        """Initialize Redis connection."""
        try:
            self.client = redis.Redis(
                host=host, port=port, db=db, password=password, decode_responses=True
            )
            self.client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise StorageError(f"Redis connection failed: {e}")

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile from storage."""
        key = f"user:{user_id}"

        try:
            data = self.client.get(key)
            if data:
                return UserProfile(**json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None

    def increment_velocity_counter(self, user_id: str) -> int:
        """Increment and get velocity counter for user."""
        key = f"velocity:{user_id}:{datetime.now().strftime('%Y%m%d%H')}"

        try:
            count = self.client.incr(key)
            self.client.expire(key, 3600)  # Expire after 1 hour
            return int(count)
        except Exception as e:
            logger.error(f"Failed to increment velocity counter: {e}")
            return 0

    def get_merchant_risk_score(self, merchant_id: str) -> float:
        """Get merchant risk score."""
        key = f"merchant:{merchant_id}:risk"

        try:
            score = self.client.get(key)
            return float(score) if score else 0.1
        except Exception as e:
            logger.error(f"Failed to get merchant risk score: {e}")
            return 0.1

    def get_user_devices(self, user_id: str) -> List[str]:
        """Get known devices for a user."""
        key = f"user:{user_id}:devices"

        try:
            devices = self.client.smembers(key)
            return list(devices) if devices else []
        except Exception as e:
            logger.error(f"Failed to get user devices: {e}")
            return []

    def add_user_device(self, user_id: str, device_id: str) -> None:
        """Add a device to user's known devices."""
        key = f"user:{user_id}:devices"

        try:
            self.client.sadd(key, device_id)
            self.client.expire(key, 86400 * 90)  # 90 days
        except Exception as e:
            logger.error(f"Failed to add user device: {e}")

    def get_recent_transaction_amounts(self, user_id: str, limit: int = 10) -> List[float]:
        """Get recent transaction amounts for a user."""
        key = f"user:{user_id}:recent_amounts"

        try:
            amounts = self.client.lrange(key, 0, limit - 1)
            return [float(a) for a in amounts] if amounts else []
        except Exception as e:
            logger.error(f"Failed to get recent amounts: {e}")
            return []

    def add_transaction_amount(self, user_id: str, amount: float) -> None:
        """Add transaction amount to recent history."""
        key = f"user:{user_id}:recent_amounts"

        try:
            self.client.lpush(key, amount)
            self.client.ltrim(key, 0, 99)  # Keep last 100
            self.client.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error(f"Failed to add transaction amount: {e}")

    def get_recent_merchants(self, user_id: str, limit: int = 10) -> List[str]:
        """Get recent merchants for a user."""
        key = f"user:{user_id}:recent_merchants"

        try:
            merchants = self.client.lrange(key, 0, limit - 1)
            return merchants if merchants else []
        except Exception as e:
            logger.error(f"Failed to get recent merchants: {e}")
            return []

    def add_merchant_interaction(self, user_id: str, merchant_id: str) -> None:
        """Add merchant to recent interactions."""
        key = f"user:{user_id}:recent_merchants"

        try:
            self.client.lpush(key, merchant_id)
            self.client.ltrim(key, 0, 99)  # Keep last 100
            self.client.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error(f"Failed to add merchant interaction: {e}")

    def get_recent_risk_scores(self, user_id: str, limit: int = 10) -> List[float]:
        """Get recent risk scores for a user."""
        key = f"user:{user_id}:risk_scores"

        try:
            scores = self.client.lrange(key, 0, limit - 1)
            return [float(s) for s in scores] if scores else []
        except Exception as e:
            logger.error(f"Failed to get recent risk scores: {e}")
            return []

    def add_risk_score(self, user_id: str, risk_score: float) -> None:
        """Add risk score to history."""
        key = f"user:{user_id}:risk_scores"

        try:
            self.client.lpush(key, risk_score)
            self.client.ltrim(key, 0, 99)  # Keep last 100
            self.client.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error(f"Failed to add risk score: {e}")

    def update_user_profile(self, user_id: str, transaction: Transaction, is_fraud: bool) -> None:
        """Update user profile with new transaction."""
        profile = self.get_user_profile(user_id) or UserProfile(user_id=user_id)

        # Update basic stats
        profile.transaction_count += 1
        profile.total_amount += transaction.amount
        profile.average_amount = profile.total_amount / profile.transaction_count
        profile.last_transaction = transaction.timestamp

        if is_fraud:
            profile.fraud_count += 1

        # Update locations
        if transaction.location and transaction.location not in profile.locations:
            profile.locations.append(transaction.location)
            # Keep only last 10 locations
            profile.locations = profile.locations[-10:]

        # Store updated profile
        key = f"user:{user_id}"
        try:
            self.client.set(key, json.dumps(profile.dict(), default=str))

            # Also update auxiliary data
            self.add_transaction_amount(user_id, transaction.amount)
            self.add_merchant_interaction(user_id, transaction.merchant_id)

            if hasattr(transaction, "device_id") and transaction.device_id:
                self.add_user_device(user_id, transaction.device_id)

        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")

    def store_transaction(
        self, transaction: Transaction, risk_score: float, ttl: int = 86400 * 7
    ) -> None:
        """Store transaction with risk score."""
        key = f"tx:{transaction.transaction_id}"
        data = {
            **transaction.dict(),
            "risk_score": risk_score,
            "processed_at": datetime.now().isoformat(),
        }

        try:
            self.client.setex(key, ttl, json.dumps(data, default=str))

            # Also add risk score to user's history
            self.add_risk_score(transaction.user_id, risk_score)

        except Exception as e:
            logger.error(f"Failed to store transaction: {e}")
            raise StorageError(f"Failed to store transaction: {e}")


class InMemoryStorage:
    """Simple in-memory storage fallback used when Redis is unavailable."""

    def __init__(self) -> None:
        self.users: Dict[str, UserProfile] = {}
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.velocity: Dict[str, int] = {}
        self.merchant_risk: Dict[str, float] = {}
        self.risk_scores: Dict[str, List[float]] = {}

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.users.get(user_id)

    def increment_velocity_counter(self, user_id: str) -> int:
        self.velocity[user_id] = self.velocity.get(user_id, 0) + 1
        return self.velocity[user_id]

    def get_merchant_risk_score(self, merchant_id: str) -> float:
        return self.merchant_risk.get(merchant_id, 0.1)

    def get_user_devices(self, user_id: str) -> List[str]:
        return []

    def add_user_device(self, user_id: str, device_id: str) -> None:
        pass

    def get_recent_transaction_amounts(self, user_id: str, limit: int = 10) -> List[float]:
        return []

    def add_transaction_amount(self, user_id: str, amount: float) -> None:
        pass

    def get_recent_merchants(self, user_id: str, limit: int = 10) -> List[str]:
        return []

    def add_merchant_interaction(self, user_id: str, merchant_id: str) -> None:
        pass

    def get_recent_risk_scores(self, user_id: str, limit: int = 10) -> List[float]:
        return self.risk_scores.get(user_id, [])[:limit]

    def add_risk_score(self, user_id: str, risk_score: float) -> None:
        self.risk_scores.setdefault(user_id, []).insert(0, risk_score)

    def update_user_profile(self, user_id: str, transaction: Transaction, is_fraud: bool) -> None:
        profile = self.get_user_profile(user_id) or UserProfile(user_id=user_id)
        profile.transaction_count += 1
        profile.total_amount += transaction.amount
        profile.average_amount = profile.total_amount / profile.transaction_count
        profile.last_transaction = transaction.timestamp
        if is_fraud:
            profile.fraud_count += 1
        if transaction.location and transaction.location not in profile.locations:
            profile.locations.append(transaction.location)
        self.users[user_id] = profile
        self.add_transaction_amount(user_id, transaction.amount)
        self.add_merchant_interaction(user_id, transaction.merchant_id)

    def store_transaction(
        self, transaction: Transaction, risk_score: float, ttl: int = 86400 * 7
    ) -> None:
        self.transactions[transaction.transaction_id] = {
            **transaction.dict(),
            "risk_score": risk_score,
            "processed_at": datetime.now().isoformat(),
        }
