# -*- coding: utf-8 -*-
"""
Custom exceptions for SLS Memory SDK.

Note: SLS SDK exceptions are passed through directly to preserve full error details.
This module only contains exceptions for SDK internal validation.
"""


class ValidationError(ValueError):
    """Raised when input validation fails in the SDK layer.
    
    This exception is raised for parameter validation before calling SLS APIs,
    such as missing required parameters (memory_id, query, etc.).
    
    For SLS service errors (authentication, not found, rate limit, etc.),
    the original SLS SDK exceptions are passed through directly.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
