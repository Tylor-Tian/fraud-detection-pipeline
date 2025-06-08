"""
Fraud Detection Pipeline

A high-performance fraud detection system with ML-powered anomaly detection.
"""

__version__ = "1.0.0"
__author__ = "Tylor Tian"
__email__ = "tylortian0@gmail.com"

from .core import FraudDetectionSystem
from .models import RiskScore, Transaction
from .exceptions import FraudDetectionError

# Compatibility patch for httpx>=0.28 used by starlette's TestClient
import inspect
import httpx

if "app" not in inspect.signature(httpx.Client.__init__).parameters:
    _orig_client_init = httpx.Client.__init__  # type: ignore

    def _client_init(self, *args, app=None, **kwargs):  # type: ignore
        _orig_client_init(self, *args, **kwargs)

    httpx.Client.__init__ = _client_init  # type: ignore

if "app" not in inspect.signature(httpx.AsyncClient.__init__).parameters:
    _orig_async_init = httpx.AsyncClient.__init__  # type: ignore

    def _async_init(self, *args, app=None, **kwargs):  # type: ignore
        _orig_async_init(self, *args, **kwargs)

    httpx.AsyncClient.__init__ = _async_init  # type: ignore

__all__ = ["FraudDetectionSystem", "RiskScore", "Transaction", "FraudDetectionError"]
