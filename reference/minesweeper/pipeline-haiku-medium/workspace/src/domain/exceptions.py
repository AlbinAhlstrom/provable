"""
Domain Layer Exceptions.
Pure domain exceptions representing business rule violations and concurrency conflicts.
"""

class DomainError(Exception):
    """Base domain error."""
    pass

class StaleDataError(DomainError):
    """Raised when an optimistic concurrency control (OCC) version conflict occurs."""
    pass

class InvariantViolation(DomainError):
    """Raised when an entity invariant is violated."""
    pass

class MaintenanceRequiredError(DomainError):
    """Raised when equipment operating hours exceed threshold before maintenance."""
    pass

class MaintenanceLockoutError(DomainError):
    """Raised when equipment is locked for maintenance."""
    pass

class ReservationConflictError(DomainError):
    """Raised when an asset is double-booked or already reserved."""
    pass

class BusinessRuleViolation(DomainError):
    """Raised when general business rules are breached."""
    pass
