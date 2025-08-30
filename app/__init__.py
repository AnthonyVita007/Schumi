"""
Flask Application Factory

This module initializes the Flask application with all necessary configurations,
database setup, and route registrations. It follows the application factory pattern
for better organization and testability.

Author: Schumi Development Team
Date: 2024
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name='default'):
    """
    Application factory function that creates and configures a Flask application instance.
    
    Args:
        config_name (str): Configuration environment name (default, development, production)
        
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Create Flask application instance
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    from .config import Config
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints/routes
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    # Create database tables within application context
    with app.app_context():
        db.create_all()
        
        # Initialize with sample data if database is empty
        from .models import Driver, Classification, MonitoringStatus
        if Driver.query.count() == 0:
            _initialize_sample_data()
    
    return app

def _initialize_sample_data():
    """
    Initialize the database with sample driver data for demonstration purposes.
    This function creates three sample drivers with different classifications and statuses.
    """
    from .models import Driver, Classification, MonitoringStatus
    
    # Sample drivers data
    sample_drivers = [
        {
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'classification': Classification.EFFICIENT,
            'monitoring_status': MonitoringStatus.OFFLINE,
            'simulation_file': 'sim_mario_rossi.csv'
        },
        {
            'first_name': 'Giulia',
            'last_name': 'Bianchi',
            'classification': Classification.UNCLASSIFIED,
            'monitoring_status': MonitoringStatus.ONLINE,
            'simulation_file': 'sim_giulia_bianchi.csv'
        },
        {
            'first_name': 'Luca',
            'last_name': 'Verdi',
            'classification': Classification.BEGINNER,
            'monitoring_status': MonitoringStatus.OFFLINE,
            'simulation_file': 'sim_luca_verdi.csv'
        }
    ]
    
    # Create and add sample drivers to database
    for driver_data in sample_drivers:
        driver = Driver(
            first_name=driver_data['first_name'],
            last_name=driver_data['last_name'],
            classification=driver_data['classification'],
            monitoring_status=driver_data['monitoring_status'],
            simulation_file=driver_data['simulation_file']
        )
        db.session.add(driver)
    
    # Commit changes to database
    db.session.commit()