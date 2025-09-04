"""
Database Models

This module defines the SQLAlchemy models for the driver management system.
It follows Object-Oriented Programming principles with well-defined classes
for representing drivers, classifications, and monitoring sessions.

Author: Schumi Development Team
Date: 2025
"""

from datetime import datetime
from enum import Enum
from . import db

class Classification(Enum):
    """
    Enumeration for driver classification types.
    
    This enum defines the possible classifications a driver can receive
    after their simulation data has been analyzed by the ML model.
    """
    UNCLASSIFIED = "Non Classificato"
    BEGINNER = "Principiante"
    EFFICIENT = "Efficiente"
    EXPERT = "Esperto"
    
    def __str__(self):
        return self.value

class MonitoringStatus(Enum):
    """
    Enumeration for driver monitoring status.
    
    This enum tracks the current monitoring state of a driver,
    indicating whether they are being monitored or available for monitoring.
    """
    OFFLINE = "Offline"
    ONLINE = "Online"
    MONITORING = "In Corso"
    
    def __str__(self):
        return self.value

class Driver(db.Model):
    """
    Driver model representing an individual driver in the system.
    
    This class encapsulates all driver-related data including personal information,
    classification results, monitoring status, and associated simulation files.
    
    Attributes:
        id (int): Primary key identifier for the driver
        first_name (str): Driver's first name
        last_name (str): Driver's last name
        classification (Classification): Current classification status
        monitoring_status (MonitoringStatus): Current monitoring state
        simulation_file (str): Path/name of the associated simulation CSV file
        created_at (datetime): Timestamp when the driver was registered
        updated_at (datetime): Timestamp of the last update
    """
    
    __tablename__ = 'drivers'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Classification and status using Enum types
    classification = db.Column(db.Enum(Classification), 
                             default=Classification.UNCLASSIFIED, 
                             nullable=False)
    monitoring_status = db.Column(db.Enum(MonitoringStatus), 
                                default=MonitoringStatus.OFFLINE, 
                                nullable=False)
    
    # File information
    simulation_file = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    classification_results = db.relationship('ClassificationResult', 
                                           backref='driver', 
                                           lazy=True, 
                                           cascade='all, delete-orphan')
    monitoring_sessions = db.relationship('MonitoringSession', 
                                        backref='driver', 
                                        lazy=True, 
                                        cascade='all, delete-orphan')
    
    def __init__(self, first_name, last_name, classification=Classification.UNCLASSIFIED, 
                 monitoring_status=MonitoringStatus.OFFLINE, simulation_file=None):
        """
        Initialize a new Driver instance.
        
        Args:
            first_name (str): Driver's first name
            last_name (str): Driver's last name
            classification (Classification): Initial classification (default: UNCLASSIFIED)
            monitoring_status (MonitoringStatus): Initial monitoring status (default: OFFLINE)
            simulation_file (str, optional): Associated simulation file name
        """
        self.first_name = first_name
        self.last_name = last_name
        self.classification = classification
        self.monitoring_status = monitoring_status
        self.simulation_file = simulation_file
    
    def get_full_name(self):
        """
        Get the driver's full name.
        
        Returns:
            str: Full name in "First Last" format
        """
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """
        Convert the driver object to a dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of the driver
        """
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'classification': self.classification.value,
            'monitoringStatus': self.monitoring_status.value,
            'simulationFile': self.simulation_file,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_classification(self, new_classification):
        """
        Update the driver's classification and record the change.
        
        Args:
            new_classification (Classification): New classification to assign
        """
        old_classification = self.classification
        self.classification = new_classification
        self.updated_at = datetime.utcnow()
        
        # Create a classification result record
        result = ClassificationResult(
            driver_id=self.id,
            old_classification=old_classification,
            new_classification=new_classification
        )
        db.session.add(result)
    
    def update_monitoring_status(self, new_status):
        """
        Update the driver's monitoring status.
        
        Args:
            new_status (MonitoringStatus): New monitoring status to assign
        """
        self.monitoring_status = new_status
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        """String representation of the Driver object."""
        return f'<Driver {self.id}: {self.get_full_name()}>'

class SimulationData(db.Model):
    """
    Model for storing simulation data extracted from CSV files.
    
    This class represents the data points collected during a driver's
    simulation session, which will be used for classification.
    
    Attributes:
        id (int): Primary key identifier
        driver_id (int): Foreign key reference to the associated driver
        file_path (str): Path to the original CSV file
        data_points (int): Number of data points in the simulation
        duration (float): Duration of the simulation in seconds
        average_speed (float): Average speed during simulation
        processed_at (datetime): When the data was processed
    """
    
    __tablename__ = 'simulation_data'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    data_points = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Float, nullable=True)
    average_speed = db.Column(db.Float, nullable=True)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, driver_id, file_path, data_points=None, 
                 duration=None, average_speed=None):
        """
        Initialize a new SimulationData instance.
        
        Args:
            driver_id (int): ID of the associated driver
            file_path (str): Path to the CSV file
            data_points (int, optional): Number of data points
            duration (float, optional): Simulation duration
            average_speed (float, optional): Average speed
        """
        self.driver_id = driver_id
        self.file_path = file_path
        self.data_points = data_points
        self.duration = duration
        self.average_speed = average_speed
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'driverId': self.driver_id,
            'filePath': self.file_path,
            'dataPoints': self.data_points,
            'duration': self.duration,
            'averageSpeed': self.average_speed,
            'processedAt': self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __repr__(self):
        return f'<SimulationData {self.id} for Driver {self.driver_id}>'

class ClassificationResult(db.Model):
    """
    Model for storing classification results and history.
    
    This class tracks when a driver's classification changes,
    providing an audit trail of classification decisions.
    
    Attributes:
        id (int): Primary key identifier
        driver_id (int): Foreign key reference to the driver
        old_classification (Classification): Previous classification
        new_classification (Classification): New classification assigned
        confidence_score (float): Confidence level of the classification
        classified_at (datetime): When the classification was performed
    """
    
    __tablename__ = 'classification_results'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    old_classification = db.Column(db.Enum(Classification), nullable=True)
    new_classification = db.Column(db.Enum(Classification), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)
    classified_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, driver_id, new_classification, old_classification=None, 
                 confidence_score=None):
        """
        Initialize a new ClassificationResult instance.
        
        Args:
            driver_id (int): ID of the associated driver
            new_classification (Classification): New classification assigned
            old_classification (Classification, optional): Previous classification
            confidence_score (float, optional): Confidence level (0.0 to 1.0)
        """
        self.driver_id = driver_id
        self.old_classification = old_classification
        self.new_classification = new_classification
        self.confidence_score = confidence_score
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'driverId': self.driver_id,
            'oldClassification': self.old_classification.value if self.old_classification else None,
            'newClassification': self.new_classification.value,
            'confidenceScore': self.confidence_score,
            'classifiedAt': self.classified_at.isoformat() if self.classified_at else None
        }
    
    def __repr__(self):
        return f'<ClassificationResult {self.id}: {self.new_classification.value}>'

class MonitoringSession(db.Model):
    """
    Model for tracking real-time monitoring sessions.
    
    This class represents individual monitoring sessions where
    a driver's emotional state and behavior are tracked in real-time.
    
    Attributes:
        id (int): Primary key identifier
        driver_id (int): Foreign key reference to the driver
        started_at (datetime): When the monitoring session began
        ended_at (datetime): When the monitoring session ended
        status (str): Current status of the session
        emotion_data_points (int): Number of emotion data points collected
    """
    
    __tablename__ = 'monitoring_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)
    emotion_data_points = db.Column(db.Integer, default=0, nullable=False)
    
    def __init__(self, driver_id, status='active'):
        """
        Initialize a new MonitoringSession instance.
        
        Args:
            driver_id (int): ID of the associated driver
            status (str): Initial status (default: 'active')
        """
        self.driver_id = driver_id
        self.status = status
    
    def end_session(self):
        """Mark the monitoring session as ended."""
        self.ended_at = datetime.utcnow()
        self.status = 'completed'
    
    def get_duration(self):
        """
        Calculate the duration of the monitoring session.
        
        Returns:
            float: Duration in seconds, or None if session is still active
        """
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'driverId': self.driver_id,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'endedAt': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status,
            'emotionDataPoints': self.emotion_data_points,
            'duration': self.get_duration()
        }
    
    def __repr__(self):
        return f'<MonitoringSession {self.id} for Driver {self.driver_id}>'