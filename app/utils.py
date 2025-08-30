"""
Utility Functions

This module contains utility functions and helper methods used throughout
the driver management system. These functions provide common functionality
for data validation, formatting, and other operations.

Author: Schumi Development Team
Date: 2024
"""

import re
import os
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class ValidationUtils:
    """
    Utility class for data validation operations.
    
    This class provides static methods for validating various types of input data
    including names, file formats, and other user inputs.
    """
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate if a name contains only allowed characters.
        
        Args:
            name (str): The name to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not name or len(name.strip()) < 2:
            return False
        
        # Allow letters, spaces, apostrophes, and hyphens
        pattern = r"^[a-zA-ZÀ-ÿ\s'-]+$"
        return bool(re.match(pattern, name.strip()))
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 16) -> bool:
        """
        Validate if file size is within allowed limits.
        
        Args:
            file_size (int): File size in bytes
            max_size_mb (int): Maximum allowed size in MB
            
        Returns:
            bool: True if valid, False otherwise
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename by removing or replacing invalid characters.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove path separators and other dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 200:
            name = name[:200]
        
        return f"{name}{ext}"


class FormatUtils:
    """
    Utility class for data formatting operations.
    
    This class provides methods for formatting data for display in the user interface.
    """
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes (int): File size in bytes
            
        Returns:
            str: Formatted file size (e.g., "1.5 MB")
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds (float): Duration in seconds
            
        Returns:
            str: Formatted duration (e.g., "2m 30s")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def format_datetime(dt: datetime, format_type: str = 'default') -> str:
        """
        Format datetime for display.
        
        Args:
            dt (datetime): Datetime object to format
            format_type (str): Format type ('default', 'short', 'time_only')
            
        Returns:
            str: Formatted datetime string
        """
        if format_type == 'short':
            return dt.strftime('%d/%m/%Y %H:%M')
        elif format_type == 'time_only':
            return dt.strftime('%H:%M:%S')
        else:
            return dt.strftime('%d/%m/%Y %H:%M:%S')
    
    @staticmethod
    def format_classification(classification_value: str) -> Dict[str, str]:
        """
        Format classification with appropriate styling information.
        
        Args:
            classification_value (str): Classification value
            
        Returns:
            Dict[str, str]: Classification with CSS class and color
        """
        classification_styles = {
            'Non Classificato': {'class': 'unclassified', 'color': '#6B7280'},
            'Principiante': {'class': 'beginner', 'color': '#F59E0B'},
            'Efficiente': {'class': 'efficient', 'color': '#3B82F6'},
            'Esperto': {'class': 'expert', 'color': '#10B981'}
        }
        
        return classification_styles.get(classification_value, {
            'class': 'unknown',
            'color': '#6B7280'
        })


class SecurityUtils:
    """
    Utility class for security-related operations.
    
    This class provides methods for generating secure identifiers,
    hashing, and other security-related functionality.
    """
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length (int): Length of the token in bytes
            
        Returns:
            str: Hexadecimal representation of the secure token
        """
        return os.urandom(length).hex()
    
    @staticmethod
    def hash_file_content(file_path: str) -> str:
        """
        Generate MD5 hash of file content.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: MD5 hash of the file content
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 255) -> str:
        """
        Sanitize user input by removing potentially dangerous content.
        
        Args:
            input_string (str): Input string to sanitize
            max_length (int): Maximum allowed length
            
        Returns:
            str: Sanitized input string
        """
        if not input_string:
            return ""
        
        # Remove potential HTML/script tags
        sanitized = re.sub(r'<[^>]*>', '', input_string)
        
        # Remove null bytes and other control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
        
        # Trim whitespace and limit length
        sanitized = sanitized.strip()[:max_length]
        
        return sanitized


class CSVUtils:
    """
    Utility class for CSV file operations.
    
    This class provides methods for reading, validating, and processing CSV files
    containing simulation data.
    """
    
    @staticmethod
    def validate_csv_structure(file_path: str, required_columns: Optional[List[str]] = None) -> bool:
        """
        Validate the structure of a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            required_columns (List[str], optional): List of required column names
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader, None)
                
                if not header:
                    return False
                
                # Check for required columns if specified
                if required_columns:
                    header_lower = [col.lower().strip() for col in header]
                    required_lower = [col.lower().strip() for col in required_columns]
                    
                    for required_col in required_lower:
                        if required_col not in header_lower:
                            return False
                
                # Check if there's at least one data row
                try:
                    next(csv_reader)
                    return True
                except StopIteration:
                    return False
                    
        except Exception:
            return False
    
    @staticmethod
    def count_csv_rows(file_path: str) -> int:
        """
        Count the number of data rows in a CSV file (excluding header).
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            int: Number of data rows
        """
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader, None)  # Skip header
                return sum(1 for row in csv_reader)
                
        except Exception:
            return 0
    
    @staticmethod
    def preview_csv_data(file_path: str, max_rows: int = 5) -> Dict[str, Any]:
        """
        Get a preview of CSV file data.
        
        Args:
            file_path (str): Path to the CSV file
            max_rows (int): Maximum number of rows to preview
            
        Returns:
            Dict[str, Any]: Preview data including headers and sample rows
        """
        try:
            import csv
            
            preview_data = {
                'headers': [],
                'rows': [],
                'total_rows': 0,
                'valid': True,
                'error': None
            }
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                # Read header
                header = next(csv_reader, None)
                if header:
                    preview_data['headers'] = header
                
                # Read sample rows
                for i, row in enumerate(csv_reader):
                    if i < max_rows:
                        preview_data['rows'].append(row)
                    preview_data['total_rows'] += 1
            
            return preview_data
            
        except Exception as e:
            return {
                'headers': [],
                'rows': [],
                'total_rows': 0,
                'valid': False,
                'error': str(e)
            }


class ResponseUtils:
    """
    Utility class for standardizing API responses.
    
    This class provides methods for creating consistent JSON responses
    across all API endpoints.
    """
    
    @staticmethod
    def success_response(data: Any = None, message: str = "", status_code: int = 200) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            data (Any): Response data
            message (str): Success message
            status_code (int): HTTP status code
            
        Returns:
            Dict[str, Any]: Standardized success response
        """
        response = {
            'success': True,
            'status_code': status_code
        }
        
        if data is not None:
            response['data'] = data
        
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def error_response(error: str, status_code: int = 400, details: Any = None) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            error (str): Error message
            status_code (int): HTTP status code
            details (Any): Additional error details
            
        Returns:
            Dict[str, Any]: Standardized error response
        """
        response = {
            'success': False,
            'error': error,
            'status_code': status_code
        }
        
        if details is not None:
            response['details'] = details
        
        return response