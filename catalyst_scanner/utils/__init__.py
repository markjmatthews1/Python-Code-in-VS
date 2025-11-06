"""
Catalyst Scanner Utilities Module

Contains logging, error handling, and other utility functions.
"""

from .logger import (
    get_logger, initialize_logging, log_startup, log_shutdown,
    log_performance, log_api_call, log_data_update, log_user_action,
    log_error_with_context, PerformanceTimer
)

from .error_handler import (
    CatalystErrorHandler, CatalystError, APIError, DataError, 
    GUIError, handle_error, get_error_handler, ErrorContext,
    error_handler, api_error_handler, data_error_handler, gui_error_handler
)

__all__ = [
    # Logging
    'get_logger', 'initialize_logging', 'log_startup', 'log_shutdown',
    'log_performance', 'log_api_call', 'log_data_update', 'log_user_action',
    'log_error_with_context', 'PerformanceTimer',
    
    # Error Handling
    'CatalystErrorHandler', 'CatalystError', 'APIError', 'DataError',
    'GUIError', 'handle_error', 'get_error_handler', 'ErrorContext',
    'error_handler', 'api_error_handler', 'data_error_handler', 'gui_error_handler'
]