"""
Application Routes and API Endpoints

This module defines all the HTTP routes for the driver management system.
It includes both web page routes for serving HTML templates and API endpoints
for AJAX communication with the frontend JavaScript.

Author: Schumi Development Team
Date: 2024
"""

import os
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from werkzeug.exceptions import BadRequest

from .services import (
    DriverService, 
    ClassificationService, 
    MonitoringService, 
    FileUploadService
)
from .models import Classification, MonitoringStatus

# Create Blueprint for main routes
main_bp = Blueprint('main', __name__)

# ================================
# WEB PAGE ROUTES (HTML Templates)
# ================================

@main_bp.route('/')
def landing_page():
    """
    Serve the landing page of the application.
    
    This page provides an overview of the driver management system workflow
    and serves as the entry point for users.
    
    Returns:
        str: Rendered HTML template for the landing page
    """
    return render_template('landing_page.html')

@main_bp.route('/drivers')
def drivers_page():
    """
    Serve the drivers management page.
    
    This page displays all registered drivers and provides functionality
    to add new drivers and manage existing ones.
    
    Returns:
        str: Rendered HTML template for the drivers page
    """
    return render_template('drivers.html')

@main_bp.route('/monitor/<int:driver_id>')
def monitor_page(driver_id):
    """
    Serve the real-time monitoring page for a specific driver.
    
    This page provides real-time monitoring capabilities including
    webcam feed and emotional state tracking.
    
    Args:
        driver_id (int): ID of the driver to monitor
        
    Returns:
        str: Rendered HTML template for the monitoring page
    """
    # Verify that the driver exists
    driver = DriverService.get_driver_by_id(driver_id)
    if not driver:
        return render_template('error.html', 
                             error_message=f"Autista con ID {driver_id} non trovato"), 404
    
    return render_template('monitor.html', driver=driver)

# ===============================
# API ENDPOINTS (JSON Responses)
# ===============================

@main_bp.route('/api/drivers', methods=['GET'])
def api_get_drivers():
    """
    API endpoint to retrieve all drivers.
    
    Returns a JSON list of all registered drivers with their current
    status and classification information.
    
    Returns:
        Response: JSON response containing list of drivers
        
    Example Response:
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "firstName": "Mario",
                    "lastName": "Rossi",
                    "classification": "Efficiente",
                    "monitoringStatus": "Offline",
                    "simulationFile": "sim_mario_rossi.csv"
                }
            ]
        }
    """
    try:
        drivers = DriverService.get_all_drivers()
        drivers_data = [driver.to_dict() for driver in drivers]
        
        return jsonify({
            'success': True,
            'data': drivers_data,
            'count': len(drivers_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving drivers: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore nel recupero degli autisti'
        }), 500

@main_bp.route('/api/drivers', methods=['POST'])
def api_add_driver():
    """
    API endpoint to add a new driver.
    
    Accepts multipart/form-data with driver information and simulation file.
    Creates a new driver record and processes the uploaded CSV file.
    
    Expected Form Data:
        - firstName (str): Driver's first name
        - lastName (str): Driver's last name
        - simulationFile (file): CSV file containing simulation data
        
    Returns:
        Response: JSON response with created driver data or error message
        
    Example Response:
        {
            "success": true,
            "data": {
                "id": 4,
                "firstName": "Anna",
                "lastName": "Verdi",
                "classification": "Non Classificato",
                "monitoringStatus": "Offline"
            },
            "message": "Autista aggiunto con successo"
        }
    """
    try:
        # Validate request content type
        if not (request.content_type and 'multipart/form-data' in request.content_type):
            raise BadRequest("Richiesta deve essere multipart/form-data")
        
        # Extract form data
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        simulation_file = request.files.get('simulationFile')
        
        # Validate required fields
        if not first_name:
            return jsonify({
                'success': False,
                'error': 'Il nome è obbligatorio'
            }), 400
            
        if not last_name:
            return jsonify({
                'success': False,
                'error': 'Il cognome è obbligatorio'
            }), 400
        
        # Create new driver
        new_driver = DriverService.create_driver(
            first_name=first_name,
            last_name=last_name,
            simulation_file=simulation_file
        )
        
        return jsonify({
            'success': True,
            'data': new_driver.to_dict(),
            'message': 'Autista aggiunto con successo'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error adding driver: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore interno del server'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>', methods=['GET'])
def api_get_driver(driver_id):
    """
    API endpoint to retrieve a specific driver by ID.
    
    Args:
        driver_id (int): Unique identifier of the driver
        
    Returns:
        Response: JSON response with driver data or error message
        
    Example Response:
        {
            "success": true,
            "data": {
                "id": 1,
                "firstName": "Mario",
                "lastName": "Rossi",
                "classification": "Efficiente",
                "monitoringStatus": "Offline",
                "simulationFile": "sim_mario_rossi.csv",
                "createdAt": "2024-01-15T10:30:00",
                "updatedAt": "2024-01-15T10:30:00"
            }
        }
    """
    try:
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': f'Autista con ID {driver_id} non trovato'
            }), 404
        
        return jsonify({
            'success': True,
            'data': driver.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore nel recupero dell\'autista'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>', methods=['PUT', 'PATCH'])
def api_update_driver(driver_id):
    """
    API endpoint to update a driver's information.
    
    Accepts JSON or multipart/form-data with driver information and optional simulation file.
    Updates driver record and optionally processes a new uploaded CSV file.
    
    Args:
        driver_id (int): ID of the driver to update
    
    Expected JSON Data (Content-Type: application/json):
        {
            "firstName": "NewFirstName",
            "lastName": "NewLastName"
        }
    
    Expected Form Data (Content-Type: multipart/form-data):
        - firstName (str, optional): Driver's new first name
        - lastName (str, optional): Driver's new last name  
        - simulationFile (file, optional): New CSV file containing simulation data
        
    Returns:
        Response: JSON response with updated driver data or error message
        
    Example Response:
        {
            "success": true,
            "data": {
                "id": 1,
                "firstName": "Mario",
                "lastName": "Rossi", 
                "classification": "Efficiente",
                "monitoringStatus": "Offline",
                "simulationFile": "sim_mario_rossi_new.csv"
            },
            "message": "Autista aggiornato con successo"
        }
    """
    try:
        first_name = None
        last_name = None
        simulation_file = None
        
        # Handle JSON or form data
        if request.is_json:
            data = request.get_json()
            first_name = data.get('firstName', '').strip() if data.get('firstName') else None
            last_name = data.get('lastName', '').strip() if data.get('lastName') else None
        else:
            # Handle form data (potentially multipart with file)
            first_name = request.form.get('firstName', '').strip() if request.form.get('firstName') else None
            last_name = request.form.get('lastName', '').strip() if request.form.get('lastName') else None
            simulation_file = request.files.get('simulationFile')
        
        # Validate that at least one field is being updated
        if not any([first_name, last_name, simulation_file]):
            return jsonify({
                'success': False,
                'error': 'Almeno un campo deve essere fornito per l\'aggiornamento'
            }), 400
        
        # Update driver
        updated_driver = DriverService.update_driver(
            driver_id=driver_id,
            first_name=first_name,
            last_name=last_name,
            simulation_file=simulation_file
        )
        
        return jsonify({
            'success': True,
            'data': updated_driver.to_dict(),
            'message': 'Autista aggiornato con successo'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error updating driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore interno del server'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
def api_delete_driver(driver_id):
    """
    API endpoint to delete a driver from the system.
    
    Deletes the driver record and any associated simulation files.
    
    Args:
        driver_id (int): ID of the driver to delete
        
    Returns:
        Response: JSON response confirming deletion or error message
        
    Example Response:
        {
            "success": true,
            "message": "Autista eliminato con successo"
        }
    """
    try:
        success = DriverService.delete_driver(driver_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': f'Autista con ID {driver_id} non trovato'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Autista eliminato con successo'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore interno del server'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>/classify', methods=['GET'])
def api_classify_driver(driver_id):
    """
    API endpoint to classify a driver based on their simulation data.
    
    This endpoint simulates the execution of a machine learning classifier
    that analyzes the driver's CSV simulation data to determine their driving style.
    
    Args:
        driver_id (int): ID of the driver to classify
        
    Returns:
        Response: JSON response with classification result
        
    Example Response:
        {
            "success": true,
            "data": {
                "classification": "Esperto",
                "confidence": 0.87,
                "previousClassification": "Non Classificato"
            },
            "message": "Classificazione completata con successo"
        }
    """
    try:
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': f'Autista con ID {driver_id} non trovato'
            }), 404
        
        # Store previous classification for response
        previous_classification = driver.classification.value
        
        # Perform classification
        new_classification, confidence = ClassificationService.classify_driver(driver_id)
        
        return jsonify({
            'success': True,
            'data': {
                'classification': new_classification.value,
                'confidence': round(confidence, 2),
                'previousClassification': previous_classification
            },
            'message': 'Classificazione completata con successo'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error classifying driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore durante la classificazione'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>/monitor', methods=['GET'])
def api_get_monitoring_data(driver_id):
    """
    API endpoint to retrieve monitoring data for a driver.
    
    This endpoint prepares the data necessary for the monitoring page
    and returns current monitoring status information.
    
    Args:
        driver_id (int): ID of the driver to monitor
        
    Returns:
        Response: JSON response with monitoring data
        
    Example Response:
        {
            "success": true,
            "data": {
                "driver": {...},
                "monitoringStatus": "Online",
                "canStartMonitoring": true
            }
        }
    """
    try:
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': f'Autista con ID {driver_id} non trovato'
            }), 404
        
        # Determine if monitoring can be started
        can_start_monitoring = driver.monitoring_status in [
            MonitoringStatus.OFFLINE, 
            MonitoringStatus.ONLINE
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'driver': driver.to_dict(),
                'monitoringStatus': driver.monitoring_status.value,
                'canStartMonitoring': can_start_monitoring
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting monitoring data for driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore nel recupero dei dati di monitoraggio'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>/monitor/start', methods=['POST'])
def api_start_monitoring(driver_id):
    """
    API endpoint to start monitoring a driver.
    
    Args:
        driver_id (int): ID of the driver to start monitoring
        
    Returns:
        Response: JSON response confirming monitoring start
    """
    try:
        MonitoringService.start_monitoring_session(driver_id)
        
        return jsonify({
            'success': True,
            'message': 'Monitoraggio avviato con successo'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error starting monitoring for driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore nell\'avvio del monitoraggio'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>/monitor/stop', methods=['POST'])
def api_stop_monitoring(driver_id):
    """
    API endpoint to stop monitoring a driver.
    
    Args:
        driver_id (int): ID of the driver to stop monitoring
        
    Returns:
        Response: JSON response confirming monitoring stop
    """
    try:
        MonitoringService.stop_monitoring_session(driver_id)
        
        return jsonify({
            'success': True,
            'message': 'Monitoraggio interrotto'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error stopping monitoring for driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore nell\'interruzione del monitoraggio'
        }), 500

@main_bp.route('/api/drivers/<int:driver_id>/monitor/data', methods=['GET'])
def api_get_realtime_emotion_data(driver_id):
    """
    API endpoint to get real-time emotion data for a monitoring session.
    
    This endpoint simulates the reception of real-time emotional analysis data
    that would be generated from computer vision analysis of the driver's webcam feed.
    
    Args:
        driver_id (int): ID of the driver being monitored
        
    Returns:
        Response: JSON response with current emotion data
        
    Example Response:
        {
            "success": true,
            "data": {
                "time": "14:35:22",
                "stress": 15.3,
                "focus": 78.9,
                "calm": 65.2,
                "timestamp": 1642689322.123
            }
        }
    """
    try:
        # Verify driver exists and is being monitored
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return jsonify({
                'success': False,
                'error': f'Autista con ID {driver_id} non trovato'
            }), 404
        
        # Generate simulated emotion data
        emotion_data = MonitoringService.generate_emotion_data()
        
        return jsonify({
            'success': True,
            'data': emotion_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting emotion data for driver {driver_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Errore nel recupero dei dati emotivi'
        }), 500

# ========================
# ERROR HANDLERS
# ========================

@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors by returning a JSON response for API calls or HTML for page requests."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint non trovato'
        }), 404
    else:
        return render_template('error.html', 
                             error_message="Pagina non trovata"), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors by returning appropriate responses."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Errore interno del server'
        }), 500
    else:
        return render_template('error.html', 
                             error_message="Errore interno del server"), 500

# ========================
# UTILITY ENDPOINTS
# ========================

@main_bp.route('/api/health', methods=['GET'])
def api_health_check():
    """
    Health check endpoint for monitoring application status.
    
    Returns:
        Response: JSON response indicating application health
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'Driver Management System is running'
    })

@main_bp.route('/favicon.ico')
def favicon():
    """Serve favicon.ico file."""
    return send_from_directory(
        os.path.join(current_app.root_path, '../static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )