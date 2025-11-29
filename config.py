"""
Configuration settings for the application
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # AI Provider Configuration
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openrouter')  # 'openai' or 'openrouter'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    
    # Model configuration - defaults based on provider
    _default_model = 'openai/gpt-4' if os.environ.get('AI_PROVIDER', 'openrouter') == 'openrouter' else 'gpt-4'
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or _default_model
    
    # Flask settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Directories
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

