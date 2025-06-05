"""
Configuration management for RAG API Client
"""

import os
from typing import Optional
from pathlib import Path


class Config:
    """
    Configuration class that handles environment variables and default settings.
    """

    def __init__(self, override_base_url: Optional[str] = None,
                 override_api_key:  Optional[str] = None,):
        """Initialize configuration from environment variables."""
        self._load_env_file()

        # API Configuration

        if override_base_url is not None:
            self.base_url = override_base_url
        else:
            self.base_url = os.getenv(
                'VIDAVOX_API_BASE_URL', 'http://localhost:8002')

        if override_api_key is not None:
            self.api_key = override_api_key
        else:
            self.api_key = os.getenv('VIDAVOX_API_KEY', '')

        # Client Configuration
        self.timeout = int(os.getenv('VIDAVOX_API_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('VIDAVOX_API_MAX_RETRIES', '3'))
        self.chunk_size = int(os.getenv('VIDAVOX_API_CHUNK_SIZE', '8192'))

        # Logging Configuration
        self.log_level = os.getenv('RAG_LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('RAG_LOG_FILE', '')

        # Validation
        self._validate_config()

    def _load_env_file(self, env_file: Optional[str] = None):
        """
        Load environment variables from .env file.

        Args:
            env_file: Path to .env file (defaults to .env in current directory)
        """
        if env_file is None:
            env_file = Path('.env')
        else:
            env_file = Path(env_file)

        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value

    def _validate_config(self):
        """Validate configuration settings."""
        if not self.base_url:
            raise ValueError("RAG_API_BASE_URL is required")

        if not self.api_key:
            raise ValueError("VIDAVOX_API_KEY is required")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'base_url': self.base_url,
            'api_key': '***' if self.api_key else None,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'chunk_size': self.chunk_size,
            'log_level': self.log_level,
            'log_file': self.log_file
        }

    def __repr__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        return f"Config({config_dict})"
