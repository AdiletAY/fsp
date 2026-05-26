__all__ = ("DomainError", "NotFoundError")


class DomainError(Exception):
    """Business / domain layer errors."""


class NotFoundError(DomainError):
    """Raised when a requested resource cannot be found."""
