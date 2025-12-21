# config.py

import os

class BaseConfig:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace_with_a_secret_key')
    SESSION_COOKIE_NAME = "chess_session"

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True  # Enables testing mode
    # Add dev-specific configs here if needed

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    # Add production-specific configs here, e.g., database URIs