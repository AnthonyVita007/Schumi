"""
Application Configuration

This module contains configuration classes for the Flask application.
It handles database connections, secret keys, and environment-specific settings.

Author: Schumi Development Team
Date: 2024
"""

import os
from pathlib import Path

class Config:
    """
    Base configuration class containing common settings for all environments.
    
    This class defines default configuration values that can be overridden
    by environment-specific configuration classes or environment variables.
    """
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # Using SQLite for simplicity and portability
    basedir = Path(__file__).parent.parent.absolute()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{basedir / "database.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable event system to save memory
    
    # File upload configuration
    UPLOAD_FOLDER = basedir / 'data' / 'simulations'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'csv'}  # Only allow CSV files for simulation data
    
    # Application-specific configuration
    DRIVERS_PER_PAGE = 20  # Pagination setting for drivers list
    MONITORING_UPDATE_INTERVAL = 3  # Seconds between monitoring data updates
    
    # AI/ML configuration for emotion detection
    EMOTION_MODEL_PATH = os.environ.get('EMOTION_MODEL_PATH') or (basedir / 'app' / 'ai' / 'models' / 'frank_emotion_detector_model.keras')
    HAAR_CASCADE_PATH = os.environ.get('HAAR_CASCADE_PATH') or (basedir / 'app' / 'ai' / 'haarcascades' / 'haarcascade_frontalface_default.xml')
    
    @staticmethod
    def validate_file_extension(filename):
        """
        Validate if the uploaded file has an allowed extension.
        
        Args:
            filename (str): Name of the uploaded file
            
        Returns:
            bool: True if file extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Enables debug mode and uses development-specific settings.
    """
    DEBUG = True
    
class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Disables debug mode and uses production-specific settings.
    """
    DEBUG = False
    
class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Uses in-memory database and enables testing mode.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration mapping for easy selection
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}