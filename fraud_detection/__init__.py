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

__all__ = ["FraudDetectionSystem", "RiskScore", "Transaction", "FraudDetectionError"]


