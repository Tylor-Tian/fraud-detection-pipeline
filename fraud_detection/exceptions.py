"""Custom exceptions for fraud detection system."""


class FraudDetectionError(Exception):
    """Base exception for fraud detection system."""
    pass


class ConfigurationError(FraudDetectionError):
    """Raised when configuration is invalid."""
    pass


class ModelError(FraudDetectionError):
    """Raised when ML model operations fail."""
    pass


class DataValidationError(FraudDetectionError):
    """Raised when input data validation fails."""
    pass


class StorageError(FraudDetectionError):
    """Raised when storage operations fail."""
    pass


