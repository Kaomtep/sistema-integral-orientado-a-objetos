"""
Custom exception hierarchy for Software FJ.

All application-specific errors inherit from SoftwareFJError.
This allows catching any system error with a single except clause
while still permitting fine-grained handling.
"""


class SoftwareFJError(Exception):
    """Base exception for the entire Software FJ system."""

    def __init__(self, message: str, code: str = "SFJ-000") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationError(SoftwareFJError):
    """Raised when input data fails validation rules."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        detail = f"{message} (field: {field})" if field else message
        super().__init__(detail, code="SFJ-VAL")


class DuplicateError(SoftwareFJError):
    """Raised when attempting to register a duplicate entity."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        super().__init__(
            f"{entity_type} with identifier '{identifier}' already exists.",
            code="SFJ-DUP",
        )


class NotFoundError(SoftwareFJError):
    """Raised when a requested entity cannot be found."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        super().__init__(
            f"{entity_type} with identifier '{identifier}' was not found.",
            code="SFJ-404",
        )


class ServiceNotAvailableError(SoftwareFJError):
    """Raised when a service is not available for reservation."""

    def __init__(self, service_name: str) -> None:
        super().__init__(
            f"Service '{service_name}' is currently not available.",
            code="SFJ-SRV-NA",
        )


class InvalidStateError(SoftwareFJError):
    """Raised when an operation is not allowed in the current state."""

    def __init__(self, current_state: str, operation: str) -> None:
        super().__init__(
            f"Cannot perform '{operation}' on entity with state '{current_state}'.",
            code="SFJ-STATE",
        )


class ReservationError(SoftwareFJError):
    """General reservation-related error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="SFJ-RES")
