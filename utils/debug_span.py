"""
Ultra-granular step tracing and timing for the inference pipeline.

This module provides a DebugSpan context manager that logs START/OK/FAIL,
elapsed time, input/output keys, correlation id, and stack trace if any error occurs.
It supports usage as both a context manager and decorator.
"""

import time
import logging
import traceback
import threading
from typing import Any, Dict, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Thread-local storage for correlation ID
_thread_local = threading.local()


def set_span_id(correlation_id: str) -> None:
    """Set the correlation ID for the current thread."""
    _thread_local.correlation_id = correlation_id


def get_span_id() -> Optional[str]:
    """Get the correlation ID for the current thread."""
    return getattr(_thread_local, 'correlation_id', None)


class DebugSpan:
    """
    Context manager and decorator for ultra-granular step tracing.
    
    Features:
    - Logs START/OK/FAIL for each step
    - Tracks elapsed time
    - Logs input/output keys
    - Includes correlation ID in all logs
    - Captures stack trace on errors
    
    Usage as context manager:
        with DebugSpan("step_name", input_data={"key": "value"}):
            # do work
            pass
    
    Usage as decorator:
        @DebugSpan("step_name")
        def my_function(arg1, arg2):
            # do work
            pass
    """
    
    def __init__(self, step_name: str, input_data: Optional[Dict[str, Any]] = None):
        """
        Initialize DebugSpan.
        
        Args:
            step_name: Name of the step being traced
            input_data: Optional dictionary of input data (will log keys only)
        """
        self.step_name = step_name
        self.input_data = input_data or {}
        self.start_time = None
        self.correlation_id = get_span_id()
    
    def __enter__(self):
        """Enter the context manager."""
        self.start_time = time.time()
        input_keys = list(self.input_data.keys()) if self.input_data else []
        logger.info(
            f"⏱️  [START] {self.step_name} | corr={self.correlation_id} | input_keys={input_keys}"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        elapsed_ms = (time.time() - self.start_time) * 1000 if self.start_time else 0
        
        if exc_type is None:
            # Success
            logger.info(
                f"✅ [OK] {self.step_name} | corr={self.correlation_id} | elapsed={elapsed_ms:.2f}ms"
            )
        else:
            # Failure
            error_msg = str(exc_val) if exc_val else "Unknown error"
            stack = ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
            logger.error(
                f"❌ [FAIL] {self.step_name} | corr={self.correlation_id} | "
                f"elapsed={elapsed_ms:.2f}ms | error={error_msg}"
            )
            logger.error(f"Stack trace:\n{stack}")
        
        # Don't suppress the exception
        return False
    
    def __call__(self, func: Callable) -> Callable:
        """Use DebugSpan as a decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract input data from function arguments
            input_data = {}
            if args:
                input_data['args_count'] = len(args)
            if kwargs:
                input_data.update({f'kwarg_{k}': type(v).__name__ for k, v in kwargs.items()})
            
            with DebugSpan(self.step_name or func.__name__, input_data=input_data):
                result = func(*args, **kwargs)
            
            # Log output info
            if result is not None:
                output_info = type(result).__name__
                if isinstance(result, dict):
                    output_info = f"dict[{len(result)} keys]"
                elif isinstance(result, (list, tuple)):
                    output_info = f"{type(result).__name__}[{len(result)} items]"
                logger.info(
                    f"🔍 [OUTPUT] {self.step_name or func.__name__} | "
                    f"corr={get_span_id()} | output={output_info}"
                )
            
            return result
        
        return wrapper
