"""Configuration management for fraud detection system."""

import os
from typing import Dict, Any, Optional
import yaml  # type: ignore
from pydantic import BaseSettings, Field
from pathlib import Path


class RedisConfig(BaseSettings):
    """Redis configuration."""

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    class Config:
        env_prefix = "REDIS_"


class KafkaConfig(BaseSettings):
    """Kafka configuration."""

    bootstrap_servers: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    input_topic: str = Field(default="transactions", env="KAFKA_INPUT_TOPIC")
    output_topic: str = Field(default="fraud_alerts", env="KAFKA_OUTPUT_TOPIC")
    consumer_group: str = Field(default="fraud-detector", env="KAFKA_CONSUMER_GROUP")

    class Config:
        env_prefix = "KAFKA_"


class ModelConfig(BaseSettings):
    """ML model configuration."""

    model_path: str = Field(default="models/fraud_model.pkl", env="MODEL_PATH")
    threshold: float = Field(default=0.7, env="MODEL_THRESHOLD")
    feature_version: str = Field(default="v1", env="MODEL_FEATURE_VERSION")

    class Config:
        env_prefix = "MODEL_"


class RulesConfig(BaseSettings):
    """Rule engine configuration."""

    high_amount_threshold: float = Field(default=10000, env="RULES_HIGH_AMOUNT")
    velocity_limit: int = Field(default=5, env="RULES_VELOCITY_LIMIT")
    location_radius_km: float = Field(default=500, env="RULES_LOCATION_RADIUS")

    class Config:
        env_prefix = "RULES_"


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = "Fraud Detection Pipeline"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    redis: RedisConfig = RedisConfig()
    kafka: KafkaConfig = KafkaConfig()
    model: ModelConfig = ModelConfig()
    rules: RulesConfig = RulesConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def from_yaml(cls, yaml_file: str) -> "Settings":
        """Load settings from YAML file."""
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)


# Global settings instance
settings = Settings()
