"""
Domain Exceptions — High-level business rule exceptions.
"""

class DomainException(Exception):
    """Base exception for all domain business rule violations."""
    pass

class InvalidStatusTransition(DomainException):
    """Raised when an illegal requirement status transition is attempted."""
    pass
