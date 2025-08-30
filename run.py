"""
Application Entry Point

This script serves as the entry point for the Driver Management System Flask application.
It creates the Flask app instance and runs the development server.

Usage:
    python run.py

Author: Schumi Development Team
Date: 2024
"""

import os
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    """
    Run the Flask development server.
    
    This will start the application in development mode with debug enabled.
    The server will be accessible at http://localhost:5000
    """
    
    # Get configuration from environment variables
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("🚗 Driver Management System - Starting Server")
    print("=" * 60)
    print(f"📍 Server will be available at: http://localhost:{port}")
    print(f"🛠️  Debug mode: {'Enabled' if debug else 'Disabled'}")
    print(f"📂 Upload directory: {app.config.get('UPLOAD_FOLDER', 'Not configured')}")
    print(f"💾 Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print("=" * 60)
    print("🎯 Available endpoints:")
    print("   • Landing Page: /")
    print("   • Drivers Page: /drivers")
    print("   • Monitor Page: /monitor/<driver_id>")
    print("   • API Health: /api/health")
    print("=" * 60)
    
    # Run the development server
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True  # Enable threading for better performance
    )