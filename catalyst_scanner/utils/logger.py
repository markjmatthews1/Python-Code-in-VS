"""
Logging Configuration for Catalyst Scanner

Provides structured logging with multiple levels and file rotation
for debugging and monitoring the application.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import logging
import logging.handlers
import os
from datetime import datetime
import sys

class CatalystLogger:
    """Centralized logging configuration for Catalyst Scanner"""
    
    def __init__(self, log_dir="logs", app_name="catalyst_scanner"):
        """Initialize the logger with file and console output"""
        self.log_dir = log_dir
        self.app_name = app_name
        self.logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Create logger
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation (detailed logging)
        log_file = os.path.join(self.log_dir, f"{self.app_name}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler (simpler format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # Error file handler (errors only)
        error_file = os.path.join(self.log_dir, f"{self.app_name}_errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=5*1024*1024, backupCount=3  # 5MB files, keep 3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # Log the initialization
        self.logger.info(f"=== {self.app_name.upper()} LOGGING INITIALIZED ===")
        self.logger.info(f"Log directory: {os.path.abspath(self.log_dir)}")
        self.logger.debug("Debug logging enabled")
    
    def get_logger(self):
        """Get the configured logger instance"""
        return self.logger
    
    def log_startup(self, version="1.0", phase="Development"):
        """Log application startup information"""
        self.logger.info("="*60)
        self.logger.info(f"CATALYST SCANNER v{version} - {phase}")
        self.logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Python version: {sys.version.split()[0]}")
        self.logger.info(f"Platform: {sys.platform}")
        self.logger.info("="*60)
    
    def log_shutdown(self):
        """Log application shutdown"""
        self.logger.info("="*60)
        self.logger.info("CATALYST SCANNER SHUTDOWN")
        self.logger.info(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
    
    def log_performance(self, operation, duration, details=None):
        """Log performance metrics"""
        message = f"PERFORMANCE | {operation} | Duration: {duration:.3f}s"
        if details:
            message += f" | {details}"
        self.logger.info(message)
    
    def log_api_call(self, api_name, endpoint, status_code=None, response_time=None):
        """Log API calls for debugging"""
        message = f"API_CALL | {api_name} | {endpoint}"
        if status_code:
            message += f" | Status: {status_code}"
        if response_time:
            message += f" | Time: {response_time:.3f}s"
        self.logger.debug(message)
    
    def log_data_update(self, data_type, count, source=None):
        """Log data updates"""
        message = f"DATA_UPDATE | {data_type} | Count: {count}"
        if source:
            message += f" | Source: {source}"
        self.logger.info(message)
    
    def log_user_action(self, action, details=None):
        """Log user interactions"""
        message = f"USER_ACTION | {action}"
        if details:
            message += f" | {details}"
        self.logger.info(message)
    
    def log_error_with_context(self, error, context=None, exc_info=True):
        """Log errors with additional context"""
        message = f"ERROR | {str(error)}"
        if context:
            message += f" | Context: {context}"
        self.logger.error(message, exc_info=exc_info)
    
    def set_debug_mode(self, enabled=True):
        """Enable or disable debug mode"""
        level = logging.DEBUG if enabled else logging.INFO
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level)
        
        self.logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")


# Global logger instance
_global_logger = None

def get_logger():
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = CatalystLogger()
    return _global_logger.get_logger()

def initialize_logging(log_dir="logs", app_name="catalyst_scanner", debug=False):
    """Initialize the global logging system"""
    global _global_logger
    _global_logger = CatalystLogger(log_dir, app_name)
    if debug:
        _global_logger.set_debug_mode(True)
    return _global_logger

def log_startup(version="1.0", phase="Development"):
    """Log application startup"""
    if _global_logger:
        _global_logger.log_startup(version, phase)

def log_shutdown():
    """Log application shutdown"""
    if _global_logger:
        _global_logger.log_shutdown()

def log_performance(operation, duration, details=None):
    """Log performance metrics"""
    if _global_logger:
        _global_logger.log_performance(operation, duration, details)

def log_api_call(api_name, endpoint, status_code=None, response_time=None):
    """Log API calls"""
    if _global_logger:
        _global_logger.log_api_call(api_name, endpoint, status_code, response_time)

def log_data_update(data_type, count, source=None):
    """Log data updates"""
    if _global_logger:
        _global_logger.log_data_update(data_type, count, source)

def log_user_action(action, details=None):
    """Log user actions"""
    if _global_logger:
        _global_logger.log_user_action(action, details)

def log_error_with_context(error, context=None, exc_info=True):
    """Log errors with context"""
    if _global_logger:
        _global_logger.log_error_with_context(error, context, exc_info)

# Context manager for performance logging
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name, details=None):
        self.operation_name = operation_name
        self.details = details
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            log_performance(self.operation_name, duration, self.details)