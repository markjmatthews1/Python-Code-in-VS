"""
Error Handler for Catalyst Scanner

Centralized error handling with logging, user notifications,
and graceful degradation for API failures.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Optional, Callable, Any
from functools import wraps

from utils.logger import get_logger, log_error_with_context


class CatalystError(Exception):
    """Base exception for Catalyst Scanner errors"""
    pass


class APIError(CatalystError):
    """API-related errors"""
    def __init__(self, api_name: str, endpoint: str, status_code: int, message: str):
        self.api_name = api_name
        self.endpoint = endpoint
        self.status_code = status_code
        super().__init__(f"{api_name} API Error ({status_code}): {message}")


class DataError(CatalystError):
    """Data processing errors"""
    pass


class GUIError(CatalystError):
    """GUI-related errors"""
    pass


class CatalystErrorHandler:
    """Centralized error handling for the application"""
    
    def __init__(self):
        """Initialize error handler"""
        self.logger = get_logger()
        self.error_count = 0
        self.recent_errors = []
        self.max_recent_errors = 50
    
    def handle_error(self, error: Exception, context: str = None, 
                    user_message: str = None, critical: bool = False) -> bool:
        """
        Handle an error with appropriate logging and user notification
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            user_message: Optional user-friendly message
            critical: Whether this is a critical error that should stop execution
            
        Returns:
            bool: True if error was handled gracefully, False if critical
        """
        try:
            self.error_count += 1
            
            # Create error record
            error_record = {
                "timestamp": datetime.now(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "critical": critical,
                "traceback": traceback.format_exc()
            }
            
            # Add to recent errors
            self.recent_errors.append(error_record)
            if len(self.recent_errors) > self.max_recent_errors:
                self.recent_errors.pop(0)
            
            # Log the error
            log_error_with_context(error, context)
            
            # Handle based on error type
            if isinstance(error, APIError):
                self._handle_api_error(error, user_message)
            elif isinstance(error, DataError):
                self._handle_data_error(error, user_message)
            elif isinstance(error, GUIError):
                self._handle_gui_error(error, user_message)
            else:
                self._handle_generic_error(error, context, user_message)
            
            # Check if we should continue
            if critical or self._is_fatal_error(error):
                self.logger.critical(f"Fatal error encountered: {str(error)}")
                return False
            
            return True
            
        except Exception as handler_error:
            # Error in error handler - this is bad!
            print(f"CRITICAL: Error handler failed: {str(handler_error)}")
            self.logger.critical(f"Error handler failure: {str(handler_error)}")
            return False
    
    def _handle_api_error(self, error: APIError, user_message: str = None):
        """Handle API-specific errors"""
        if error.status_code == 401:
            self.logger.error("Authentication failed - token may have expired")
            default_message = "Authentication error. Please check your API credentials."
        elif error.status_code == 429:
            self.logger.warning("Rate limit exceeded - will retry later")
            default_message = "API rate limit reached. Data updates may be delayed."
        elif error.status_code >= 500:
            self.logger.error(f"{error.api_name} server error: {error.status_code}")
            default_message = f"{error.api_name} server is experiencing issues. Data may be delayed."
        else:
            self.logger.error(f"API error: {error}")
            default_message = f"API communication error with {error.api_name}."
        
        message = user_message or default_message
        self._show_user_notification(message, "warning")
    
    def _handle_data_error(self, error: DataError, user_message: str = None):
        """Handle data processing errors"""
        self.logger.error(f"Data processing error: {error}")
        message = user_message or "Data processing error occurred. Some information may be incomplete."
        self._show_user_notification(message, "warning")
    
    def _handle_gui_error(self, error: GUIError, user_message: str = None):
        """Handle GUI errors"""
        self.logger.error(f"GUI error: {error}")
        message = user_message or "Interface error occurred. Please try refreshing the display."
        self._show_user_notification(message, "error")
    
    def _handle_generic_error(self, error: Exception, context: str = None, user_message: str = None):
        """Handle generic errors"""
        self.logger.error(f"Unexpected error in {context or 'unknown location'}: {error}")
        message = user_message or "An unexpected error occurred. The application will continue running."
        self._show_user_notification(message, "error")
    
    def _is_fatal_error(self, error: Exception) -> bool:
        """Determine if an error should cause the application to exit"""
        fatal_errors = [
            SystemExit,
            KeyboardInterrupt,
            MemoryError
        ]
        
        return any(isinstance(error, fatal_type) for fatal_type in fatal_errors)
    
    def _show_user_notification(self, message: str, level: str = "info"):
        """Show user notification (can be overridden for GUI notifications)"""
        # For now, just log to console
        # This can be extended to show GUI notifications
        level_map = {
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error
        }
        
        log_func = level_map.get(level, self.logger.info)
        log_func(f"USER NOTIFICATION: {message}")
    
    def get_error_summary(self) -> dict:
        """Get summary of recent errors"""
        return {
            "total_errors": self.error_count,
            "recent_error_count": len(self.recent_errors),
            "last_error": self.recent_errors[-1] if self.recent_errors else None,
            "error_types": self._get_error_type_distribution()
        }
    
    def _get_error_type_distribution(self) -> dict:
        """Get distribution of error types"""
        distribution = {}
        for error_record in self.recent_errors:
            error_type = error_record["error_type"]
            distribution[error_type] = distribution.get(error_type, 0) + 1
        return distribution
    
    def clear_error_history(self):
        """Clear error history"""
        self.recent_errors.clear()
        self.error_count = 0
        self.logger.info("Error history cleared")


# Global error handler instance
_global_error_handler = None

def get_error_handler() -> CatalystErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = CatalystErrorHandler()
    return _global_error_handler

def handle_error(error: Exception, context: str = None, 
                user_message: str = None, critical: bool = False) -> bool:
    """Handle an error using the global error handler"""
    return get_error_handler().handle_error(error, context, user_message, critical)

def error_handler(context: str = None, user_message: str = None, 
                 critical: bool = False, reraise: bool = False):
    """
    Decorator for automatic error handling
    
    Args:
        context: Context description for the error
        user_message: User-friendly error message
        critical: Whether errors should be treated as critical
        reraise: Whether to reraise the exception after handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_context = context or f"{func.__name__}"
                handled = handle_error(e, func_context, user_message, critical)
                
                if reraise or not handled:
                    raise
                
                # Return None or empty result for graceful degradation
                return None
        return wrapper
    return decorator

# Convenience decorators for common scenarios
def api_error_handler(api_name: str = None, reraise: bool = False):
    """Decorator for API functions"""
    return error_handler(
        context=f"{api_name or 'API'} call",
        user_message=f"API communication error with {api_name or 'service'}",
        reraise=reraise
    )

def data_error_handler(operation: str = None, reraise: bool = False):
    """Decorator for data processing functions"""
    return error_handler(
        context=f"Data processing: {operation or 'unknown operation'}",
        user_message="Data processing error - some information may be incomplete",
        reraise=reraise
    )

def gui_error_handler(component: str = None, reraise: bool = False):
    """Decorator for GUI functions"""
    return error_handler(
        context=f"GUI: {component or 'unknown component'}",
        user_message="Interface error - please try refreshing",
        reraise=reraise
    )

# Context manager for error handling
class ErrorContext:
    """Context manager for handling errors in code blocks"""
    
    def __init__(self, context: str, user_message: str = None, critical: bool = False):
        self.context = context
        self.user_message = user_message
        self.critical = critical
        self.error_occurred = False
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            self.error = exc_val
            handled = handle_error(exc_val, self.context, self.user_message, self.critical)
            
            # Suppress exception if handled gracefully
            return handled and not self.critical
        
        return False