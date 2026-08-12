"""
Service Layer Exceptions.
"""

from domain.exceptions import DomainException

class ServiceException(Exception):
    """Base exception for Service Layer workflow failures."""
    pass

class RequirementNotFound(ServiceException):
    """Raised when a requested requirement is missing from the repository."""
    pass
