"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path
import json
from datetime import datetime
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_transaction():
    """Sample transaction for testing."""
    return {
        "transaction_id": "TEST001",
        "user_id": "USER001",
        "amount": 100.0,
        "merchant_id": "MERCH001",
        "timestamp": datetime.now().isoformat()
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    from unittest.mock import Mock
    
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.setex.return_value = True
    redis_mock.incr.return_value = 1
    redis_mock.expire.return_value = True
    redis_mock.ping.return_value = True
    
    return redis_mock


@pytest.fixture
def temp_model_file():
    """Create temporary model file for testing."""
    import joblib
    from sklearn.ensemble import IsolationForest
    
    # Create a simple model
    model = IsolationForest(contamination=0.1, random_state=42)
    X_dummy = [[0, 1], [1, 1], [1, 0], [0, 0]] * 25
    model.fit(X_dummy)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        joblib.dump(model, f.name)
        yield f.name

