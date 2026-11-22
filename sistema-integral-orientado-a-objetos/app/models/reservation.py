"""
Reservation entity that links a Client with a Service.
Implements the full state machine with robust exception handling.
"""

from __future__ import annotations

from datetime import datetime

from app.exceptions import (
    ValidationError,
    InvalidStateError,
    ServiceNotAvailableError,
    ReservationError,
)
from app.models.base import Entity
from app.models.client import Client
from app.models.service import Service, Room, Equipment, Consulting
from app.utils.logger import log_event, log_exception


class Reservation(Entity):
    """
    Represents a reservation.

    State machine:
        PENDING → CONFIRMED → FINISHED
                 ↘ CANCELLED
    """

    VALID_STATES = ("PENDING", "CONFIRMED", "FINISHED", "CANCELLED")

    def __init__(
        self,
        client: Client,
        service: Service,
        duration: float,
        notes: str = "",
    ) -> None:
        if not isinstance(client, Client):
            raise ValidationError("A valid Client instance is required.", field="client")
        if not isinstance(service, Service):
            raise ValidationError("A valid Service instance is required.", field="service")
        if duration <= 0:
            raise ValidationError("Duration must be greater than zero.", field="duration")

        super().__init__(name=f"Reservation-{client.name[:20]}")
        self._client = client
        self._service = service
        self._duration = float(duration)
        self._state = "PENDING"
        self._notes = notes
        self._calculated_cost = 0.0
        self._confirmed_at: datetime | None = None
        self._cancelled_at: datetime | None = None

        log_event(f"Reservation created (PENDING): {self.id} for {client.name}")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def client(self) -> Client:
        return self._client

    @property
    def service(self) -> Service:
        return self._service

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def state(self) -> str:
        return self._state

    @property
    def calculated_cost(self) -> float:
        return self._calculated_cost

    def validate(self) -> bool:
        if self._state not in self.VALID_STATES:
            raise ValidationError(f"Invalid state: {self._state}", field="state")
        if self._duration <= 0:
            raise ValidationError("Duration must be > 0", field="duration")
        return True

    def description(self) -> str:
        return (
            f"Reservation [{self.id}] | Client: {self._client.name} | "
            f"Service: {self._service.name} | Duration: {self._duration} | "
            f"State: {self._state} | Cost: ${self._calculated_cost:,.0f}"
        )

    # ------------------------------------------------------------------
    # Business operations
    # ------------------------------------------------------------------
    def calculate_cost(self, discount: float = 0.0, **kwargs) -> float:
        """
        Calculate cost using polymorphism.
        Each service type receives the appropriate arguments.
        """
        try:
            if isinstance(self._service, Room):
                self._calculated_cost = self._service.calculate_cost(
                    hours=self._duration, discount=discount, **kwargs
                )
            elif isinstance(self._service, Equipment):
                self._calculated_cost = self._service.calculate_cost(
                    days=int(self._duration), discount=discount, **kwargs
                )
            elif isinstance(self._service, Consulting):
                self._calculated_cost = self._service.calculate_cost(
                    hours=self._duration, discount=discount, **kwargs
                )
            else:
                self._calculated_cost = self._service.base_price * self._duration

            log_event(
                f"Cost calculated for reservation {self.id}: "
                f"${self._calculated_cost:,.0f}"
            )
            return self._calculated_cost

        except (ValidationError, ServiceNotAvailableError) as exc:
            log_exception(exc, context=f"Reservation.calculate_cost [{self.id}]")
            raise ReservationError(f"Could not calculate cost: {exc}") from exc

    def confirm(self, discount: float = 0.0, **kwargs) -> bool:
        """
        Confirm the reservation.

        Demonstrates the full try / except / else / finally pattern
        and exception chaining.
        """
        try:
            if self._state != "PENDING":
                raise InvalidStateError(self._state, "confirm")

            if not self._service.available:
                raise ServiceNotAvailableError(self._service.name)

            self.calculate_cost(discount=discount, **kwargs)

        except (InvalidStateError, ServiceNotAvailableError, ReservationError) as exc:
            log_exception(exc, context=f"Reservation.confirm [{self.id}]")
            raise
        else:
            # Executed only when no exception occurred
            self._state = "CONFIRMED"
            self._confirmed_at = datetime.now()
            log_event(
                f"Reservation {self.id} CONFIRMED. "
                f"Cost: ${self._calculated_cost:,.0f}"
            )
            return True
        finally:
            # Always executed
            log_event(
                f"Confirmation attempt finished for {self.id} "
                f"(final state: {self._state})"
            )

    def cancel(self, reason: str = "") -> bool:
        """Cancel a pending or confirmed reservation."""
        try:
            if self._state in ("FINISHED", "CANCELLED"):
                raise InvalidStateError(self._state, "cancel")

            self._state = "CANCELLED"
            self._cancelled_at = datetime.now()
            if reason:
                self._notes = f"{self._notes} | Cancelled: {reason}".strip(" |")
            log_event(f"Reservation {self.id} CANCELLED. Reason: {reason or 'N/A'}")
            return True

        except InvalidStateError as exc:
            log_exception(exc, context=f"Reservation.cancel [{self.id}]")
            raise

    def finish(self) -> bool:
        """Mark a confirmed reservation as finished."""
        try:
            if self._state != "CONFIRMED":
                raise InvalidStateError(self._state, "finish")

            self._state = "FINISHED"
            log_event(f"Reservation {self.id} FINISHED.")
            return True

        except InvalidStateError as exc:
            log_exception(exc, context=f"Reservation.finish [{self.id}]")
            raise

    def __str__(self) -> str:
        return (
            f"Reservation({self.id}, {self._client.name}, "
            f"{self._service.name}, {self._state})"
        )
