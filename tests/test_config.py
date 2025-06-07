"""Tests for configuration management."""

import pytest
import os
from pathlib import Path
import tempfile
import yaml

from fraud_detection.config import Settings, RedisConfig, KafkaConfig, ModelConfig, RulesConfig


class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_default_settings(self):
        """Test default settings initialization."""
        settings = Settings()
        
        assert settings.app_name == "Fraud Detection Pipeline"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        
        # Check nested configs
        assert settings.redis.host == "localhost"
        assert settings.redis.port == 6379
        assert settings.kafka.bootstrap_servers == "localhost:9092"
        assert settings.model.threshold == 0.7
        assert settings.rules.high_amount_threshold == 10000
    
    def test_environment_variables(self):
        """Test loading from environment variables."""
        # Set environment variables
        os.environ["DEBUG"] = "true"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["REDIS_HOST"] = "redis.example.com"
        os.environ["REDIS_PORT"] = "6380"
        os.environ["MODEL_THRESHOLD"] = "0.8"
        
        try:
            settings = Settings()
            
            assert settings.debug is True
            assert settings.log_level == "DEBUG"
            assert settings.redis.host == "redis.example.com"
            assert settings.redis.port == 6380
            assert settings.model.threshold == 0.8
        finally:
            # Clean up
            for key in ["DEBUG", "LOG_LEVEL", "REDIS_HOST", "REDIS_PORT", "MODEL_THRESHOLD"]:
                os.environ.pop(key, None)
    
    def test_yaml_configuration(self):
        """Test loading from YAML file."""
        config_data = {
            "app_name": "Test Fraud Detection",
            "debug": True,
            "redis": {
                "host": "redis-test.com",
                "port": 6379,
                "db": 1
            },
            "kafka": {
                "bootstrap_servers": "kafka1:9092,kafka2:9092",
                "input_topic": "test-transactions"
            },
            "model": {
                "model_path": "test/model.pkl",
                "threshold": 0.6
            },
            "rules": {
                "high_amount_threshold": 5000,
                "velocity_limit": 3
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            f.flush()
            
            try:
                settings = Settings.from_yaml(f.name)
                
                assert settings.app_name == "Test Fraud Detection"
                assert settings.debug is True
                assert settings.redis.host == "redis-test.com"
                assert settings.redis.db == 1
                assert settings.kafka.input_topic == "test-transactions"
                assert settings.model.threshold == 0.6
                assert settings.rules.high_amount_threshold == 5000
            finally:
                os.unlink(f.name)


