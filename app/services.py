"""
Business Logic Services

This module contains the business logic for the driver management system.
It provides services for driver management, classification simulation,
and monitoring functionality following the Single Responsibility Principle.

Author: Schumi Development Team
Date: 2024
"""

import os
import random
import time
import csv
from typing import List, Dict, Optional, Tuple
from werkzeug.utils import secure_filename
from flask import current_app

from . import db
from .models import Driver, Classification, MonitoringStatus, SimulationData, ClassificationResult
from .config import Config

class DriverService:
    """
    Service class for managing driver-related operations.
    
    This class encapsulates all business logic related to drivers,
    including CRUD operations, validation, and data processing.
    """
    
    @staticmethod
    def get_all_drivers() -> List[Driver]:
        """
        Retrieve all drivers from the database.
        
        Returns:
            List[Driver]: List of all driver objects
        """
        return Driver.query.order_by(Driver.created_at.desc()).all()
    
    @staticmethod
    def get_driver_by_id(driver_id: int) -> Optional[Driver]:
        """
        Retrieve a specific driver by their ID.
        
        Args:
            driver_id (int): The unique identifier of the driver
            
        Returns:
            Optional[Driver]: Driver object if found, None otherwise
        """
        return Driver.query.get(driver_id)
    
    @staticmethod
    def create_driver(first_name: str, last_name: str, simulation_file=None) -> Driver:
        """
        Create a new driver in the system.
        
        Args:
            first_name (str): Driver's first name
            last_name (str): Driver's last name
            simulation_file (FileStorage, optional): Uploaded simulation CSV file
            
        Returns:
            Driver: The newly created driver object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate input parameters
        if not first_name or not first_name.strip():
            raise ValueError("Il nome è obbligatorio")
        
        if not last_name or not last_name.strip():
            raise ValueError("Il cognome è obbligatorio")
        
        # Clean and validate names
        first_name = first_name.strip().title()
        last_name = last_name.strip().title()
        
        # Check for duplicate drivers (same first and last name)
        existing_driver = Driver.query.filter_by(
            first_name=first_name, 
            last_name=last_name
        ).first()
        
        if existing_driver:
            raise ValueError(f"Un autista con nome {first_name} {last_name} esiste già")
        
        # Handle simulation file upload if provided
        simulation_filename = None
        if simulation_file:
            simulation_filename = FileUploadService.save_simulation_file(
                simulation_file, first_name, last_name
            )
        
        # Create new driver instance
        new_driver = Driver(
            first_name=first_name,
            last_name=last_name,
            simulation_file=simulation_filename
        )
        
        # Save to database
        db.session.add(new_driver)
        db.session.commit()
        
        # Process simulation data if file was uploaded
        if simulation_file and simulation_filename:
            SimulationDataService.process_simulation_file(
                new_driver.id, simulation_filename
            )
        
        return new_driver
    
    @staticmethod
    def update_driver_monitoring_status(driver_id: int, new_status: MonitoringStatus) -> Driver:
        """
        Update the monitoring status of a driver.
        
        Args:
            driver_id (int): ID of the driver to update
            new_status (MonitoringStatus): New monitoring status
            
        Returns:
            Driver: Updated driver object
            
        Raises:
            ValueError: If driver not found
        """
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError(f"Autista con ID {driver_id} non trovato")
        
        driver.update_monitoring_status(new_status)
        db.session.commit()
        
        return driver
    
    @staticmethod
    def delete_driver(driver_id: int) -> bool:
        """
        Delete a driver from the system.
        
        Args:
            driver_id (int): ID of the driver to delete
            
        Returns:
            bool: True if deletion was successful, False if driver not found
        """
        driver = Driver.query.get(driver_id)
        if not driver:
            return False
        
        # Delete associated simulation file if it exists
        if driver.simulation_file:
            FileUploadService.delete_simulation_file(driver.simulation_file)
        
        db.session.delete(driver)
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_driver(driver_id: int, first_name: str = None, last_name: str = None, simulation_file=None) -> Driver:
        """
        Update a driver's information.
        
        Args:
            driver_id (int): ID of the driver to update
            first_name (str, optional): New first name
            last_name (str, optional): New last name
            simulation_file (FileStorage, optional): New simulation CSV file
            
        Returns:
            Driver: Updated driver object
            
        Raises:
            ValueError: If driver not found or invalid data provided
        """
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError(f"Autista con ID {driver_id} non trovato")
        
        # Update names if provided
        if first_name is not None:
            first_name = first_name.strip().title()
            if not first_name:
                raise ValueError("Il nome non può essere vuoto")
            if len(first_name) < 2:
                raise ValueError("Il nome deve contenere almeno 2 caratteri")
            
            # Check for duplicate drivers (excluding current driver)
            existing_driver = Driver.query.filter(
                Driver.first_name == first_name,
                Driver.last_name == (last_name.strip().title() if last_name else driver.last_name),
                Driver.id != driver_id
            ).first()
            
            if existing_driver:
                raise ValueError(f"Un autista con nome {first_name} {last_name or driver.last_name} esiste già")
            
            driver.first_name = first_name
        
        if last_name is not None:
            last_name = last_name.strip().title()
            if not last_name:
                raise ValueError("Il cognome non può essere vuoto")
            if len(last_name) < 2:
                raise ValueError("Il cognome deve contenere almeno 2 caratteri")
            
            # Check for duplicate drivers (excluding current driver)
            existing_driver = Driver.query.filter(
                Driver.first_name == (first_name.strip().title() if first_name else driver.first_name),
                Driver.last_name == last_name,
                Driver.id != driver_id
            ).first()
            
            if existing_driver:
                raise ValueError(f"Un autista con nome {first_name or driver.first_name} {last_name} esiste già")
            
            driver.last_name = last_name
        
        # Handle simulation file replacement if provided
        if simulation_file:
            # Delete old file if it exists
            if driver.simulation_file:
                FileUploadService.delete_simulation_file(driver.simulation_file)
            
            # Save new file
            simulation_filename = FileUploadService.save_simulation_file(
                simulation_file, driver.first_name, driver.last_name
            )
            driver.simulation_file = simulation_filename
            
            # Process new simulation data
            SimulationDataService.process_simulation_file(driver.id, simulation_filename)
        
        db.session.commit()
        return driver

class ClassificationService:
    """
    Service class for driver classification operations.
    
    This class handles the simulation of ML-based driver classification,
    providing placeholder functionality that can be replaced with actual
    machine learning models in the future.
    """
    
    # Classification probabilities for simulation
    CLASSIFICATION_WEIGHTS = {
        Classification.BEGINNER: 0.3,
        Classification.EFFICIENT: 0.4,
        Classification.EXPERT: 0.3
    }
    
    @staticmethod
    def classify_driver(driver_id: int) -> Tuple[Classification, float]:
        """
        Classify a driver based on their simulation data.
        
        This is a placeholder implementation that randomly assigns classifications.
        In a real implementation, this would analyze the driver's CSV simulation data
        using machine learning models to determine their driving style.
        
        Args:
            driver_id (int): ID of the driver to classify
            
        Returns:
            Tuple[Classification, float]: Classification result and confidence score
            
        Raises:
            ValueError: If driver not found or no simulation data available
        """
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError(f"Autista con ID {driver_id} non trovato")
        
        if not driver.simulation_file:
            raise ValueError("Nessun file di simulazione trovato per questo autista")
        
        # Simulate processing delay (real ML would take time)
        time.sleep(random.uniform(1.5, 3.0))
        
        # Simulate classification logic
        # In real implementation, this would analyze CSV data
        classification = ClassificationService._simulate_classification_analysis()
        confidence_score = random.uniform(0.75, 0.95)  # High confidence simulation
        
        # Update driver's classification
        old_classification = driver.classification
        driver.update_classification(classification)
        
        # Create classification result record
        result = ClassificationResult(
            driver_id=driver_id,
            old_classification=old_classification,
            new_classification=classification,
            confidence_score=confidence_score
        )
        db.session.add(result)
        db.session.commit()
        
        return classification, confidence_score
    
    @staticmethod
    def _simulate_classification_analysis() -> Classification:
        """
        Simulate ML classification analysis.
        
        This method randomly selects a classification based on weighted probabilities
        to simulate the output of a machine learning model.
        
        Returns:
            Classification: Randomly selected classification
        """
        classifications = list(ClassificationService.CLASSIFICATION_WEIGHTS.keys())
        weights = list(ClassificationService.CLASSIFICATION_WEIGHTS.values())
        
        return random.choices(classifications, weights=weights)[0]
    
    @staticmethod
    def get_classification_history(driver_id: int) -> List[ClassificationResult]:
        """
        Get the classification history for a driver.
        
        Args:
            driver_id (int): ID of the driver
            
        Returns:
            List[ClassificationResult]: List of classification results ordered by date
        """
        return ClassificationResult.query.filter_by(driver_id=driver_id)\
                                       .order_by(ClassificationResult.classified_at.desc())\
                                       .all()

class SimulationDataService:
    """
    Service class for processing simulation data from CSV files.
    
    This class handles the extraction and analysis of simulation data
    uploaded by users for driver classification.
    """
    
    @staticmethod
    def process_simulation_file(driver_id: int, filename: str) -> SimulationData:
        """
        Process a simulation CSV file and extract relevant data.
        
        Args:
            driver_id (int): ID of the associated driver
            filename (str): Name of the simulation file
            
        Returns:
            SimulationData: Processed simulation data object
        """
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Analyze CSV file
            data_points, duration, avg_speed = SimulationDataService._analyze_csv_file(file_path)
            
            # Create simulation data record
            sim_data = SimulationData(
                driver_id=driver_id,
                file_path=filename,
                data_points=data_points,
                duration=duration,
                average_speed=avg_speed
            )
            
            db.session.add(sim_data)
            db.session.commit()
            
            return sim_data
            
        except Exception as e:
            current_app.logger.error(f"Error processing simulation file {filename}: {str(e)}")
            # Create basic record even if processing fails
            sim_data = SimulationData(
                driver_id=driver_id,
                file_path=filename
            )
            db.session.add(sim_data)
            db.session.commit()
            
            return sim_data
    
    @staticmethod
    def _analyze_csv_file(file_path: str) -> Tuple[int, float, float]:
        """
        Analyze a CSV simulation file to extract basic metrics.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            Tuple[int, float, float]: Data points count, duration, average speed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                # Skip header if present
                header = next(csv_reader, None)
                
                # Count data points and simulate analysis
                data_points = sum(1 for row in csv_reader)
                
                # Simulate duration and speed calculation
                # In real implementation, these would be calculated from actual CSV data
                duration = data_points * random.uniform(0.1, 0.5)  # Seconds per data point
                avg_speed = random.uniform(30, 80)  # km/h
                
                return data_points, duration, avg_speed
                
        except Exception as e:
            current_app.logger.warning(f"Could not analyze CSV file {file_path}: {str(e)}")
            # Return default values if analysis fails
            return 0, 0.0, 0.0

class FileUploadService:
    """
    Service class for handling file upload operations.
    
    This class manages the upload, validation, and storage of simulation CSV files.
    """
    
    @staticmethod
    def save_simulation_file(file, first_name: str, last_name: str) -> str:
        """
        Save an uploaded simulation file to the designated directory.
        
        Args:
            file (FileStorage): Uploaded file object
            first_name (str): Driver's first name for filename generation
            last_name (str): Driver's last name for filename generation
            
        Returns:
            str: Saved filename
            
        Raises:
            ValueError: If file is invalid or upload fails
        """
        if not file or not file.filename:
            raise ValueError("Nessun file selezionato")
        
        # Validate file extension
        if not Config.validate_file_extension(file.filename):
            raise ValueError("Solo file CSV sono permessi")
        
        # Generate secure filename
        timestamp = int(time.time())
        safe_first_name = secure_filename(first_name.lower())
        safe_last_name = secure_filename(last_name.lower())
        filename = f"sim_{safe_first_name}_{safe_last_name}_{timestamp}.csv"
        
        # Ensure upload directory exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        return filename
    
    @staticmethod
    def delete_simulation_file(filename: str) -> bool:
        """
        Delete a simulation file from storage.
        
        Args:
            filename (str): Name of the file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file {filename}: {str(e)}")
        
        return False

class MonitoringService:
    """
    Service class for real-time monitoring operations.
    
    This class handles the simulation of real-time emotional monitoring
    data that would be generated from computer vision analysis.
    """
    
    @staticmethod
    def generate_emotion_data() -> Dict[str, any]:
        """
        Generate simulated real-time emotion data.
        
        This method simulates the output that would come from a computer vision
        system analyzing a driver's facial expressions and behavior.
        
        Returns:
            Dict[str, any]: Emotion data with stress, focus, and calm levels
        """
        import datetime
        
        # Generate realistic emotion values
        # In real implementation, this would come from CV analysis
        base_stress = random.uniform(10, 30)
        base_focus = random.uniform(60, 90)
        base_calm = random.uniform(40, 70)
        
        # Add some natural variation
        stress = max(0, min(100, base_stress + random.uniform(-5, 5)))
        focus = max(0, min(100, base_focus + random.uniform(-10, 10)))
        calm = max(0, min(100, base_calm + random.uniform(-5, 5)))
        
        return {
            'time': datetime.datetime.now().strftime('%H:%M:%S'),
            'stress': round(stress, 1),
            'focus': round(focus, 1),
            'calm': round(calm, 1),
            'timestamp': time.time()
        }
    
    @staticmethod
    def start_monitoring_session(driver_id: int):
        """
        Start a new monitoring session for a driver.
        
        Args:
            driver_id (int): ID of the driver to monitor
            
        Raises:
            ValueError: If driver not found
        """
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError(f"Autista con ID {driver_id} non trovato")
        
        # Update driver status
        driver.update_monitoring_status(MonitoringStatus.MONITORING)
        db.session.commit()
    
    @staticmethod
    def stop_monitoring_session(driver_id: int):
        """
        Stop the monitoring session for a driver.
        
        Args:
            driver_id (int): ID of the driver
            
        Raises:
            ValueError: If driver not found
        """
        driver = Driver.query.get(driver_id)
        if not driver:
            raise ValueError(f"Autista con ID {driver_id} non trovato")
        
        # Update driver status
        driver.update_monitoring_status(MonitoringStatus.ONLINE)
        db.session.commit()