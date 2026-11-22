"""
Service hierarchy: abstract Service + three concrete implementations.
Demonstrates inheritance, polymorphism and method overloading.
"""

from __future__ import annotations

from abc import abstractmethod

from app.exceptions import ValidationError, ServiceNotAvailableError
from app.models.base import Entity
from app.utils.logger import log_event


class Service(Entity):
    """
    Abstract base for every service offered by Software FJ.
    Subclasses must implement `calculate_cost`.
    """

    def __init__(
        self,
        name: str,
        base_price: float,
        available: bool = True,
    ) -> None:
        super().__init__(name)
        if base_price < 0:
            raise ValidationError("Base price cannot be negative.", field="base_price")
        self._base_price: float = float(base_price)
        self._available: bool = available

    @property
    def base_price(self) -> float:
        return self._base_price

    @property
    def available(self) -> bool:
        return self._available

    def mark_available(self) -> None:
        self._available = True

    def mark_unavailable(self) -> None:
        self._available = False

    def validate(self) -> bool:
        if not self._name:
            raise ValidationError("Service name is required.", field="name")
        if self._base_price < 0:
            raise ValidationError("Base price cannot be negative.", field="base_price")
        return True

    @abstractmethod
    def calculate_cost(self, *args, **kwargs) -> float:
        """Polymorphic cost calculation (overloaded via optional parameters)."""

    def description(self) -> str:
        status = "AVAILABLE" if self._available else "UNAVAILABLE"
        return (
            f"Service [{self.id}] {self.name} | "
            f"Base price: ${self._base_price:,.0f} | Status: {status}"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, ${self._base_price:,.0f})"


# ---------------------------------------------------------------------------
# Concrete services
# ---------------------------------------------------------------------------

class Room(Service):
    """Meeting-room reservation service."""

    def __init__(
        self,
        name: str,
        base_price: float,
        capacity: int,
        has_projector: bool = False,
        available: bool = True,
    ) -> None:
        super().__init__(name, base_price, available)
        if capacity <= 0:
            raise ValidationError("Capacity must be greater than zero.", field="capacity")
        self._capacity = capacity
        self._has_projector = has_projector
        log_event(f"Room registered: {name}")

    @property
    def capacity(self) -> int:
        return self._capacity

    def calculate_cost(
        self,
        hours: float = 1,
        discount: float = 0.0,
        tax: float = 0.19,
    ) -> float:
        """
        Cost = (base_price * hours) * (1 - discount) * (1 + tax)
        """
        if hours <= 0:
            raise ValidationError("Hours must be greater than zero.", field="hours")
        if not 0 <= discount <= 1:
            raise ValidationError("Discount must be between 0 and 1.", field="discount")
        if not self._available:
            raise ServiceNotAvailableError(self.name)

        subtotal = self._base_price * hours
        after_discount = subtotal * (1 - discount)
        return round(after_discount * (1 + tax), 2)

    def description(self) -> str:
        base = super().description()
        projector = "Yes" if self._has_projector else "No"
        return f"{base} | Capacity: {self._capacity} | Projector: {projector}"


class Equipment(Service):
    """Equipment rental service."""

    def __init__(
        self,
        name: str,
        base_price: float,
        equipment_type: str,
        requires_deposit: bool = True,
        available: bool = True,
    ) -> None:
        super().__init__(name, base_price, available)
        if not equipment_type or not equipment_type.strip():
            raise ValidationError("Equipment type is required.", field="equipment_type")
        self._equipment_type = equipment_type.strip()
        self._requires_deposit = requires_deposit
        self._deposit = self._base_price * 0.30 if requires_deposit else 0.0
        log_event(f"Equipment registered: {name}")

    @property
    def equipment_type(self) -> str:
        return self._equipment_type

    def calculate_cost(
        self,
        days: int = 1,
        discount: float = 0.0,
        include_deposit: bool = True,
    ) -> float:
        """
        Cost = (base_price * days) * (1 - discount) [+ deposit]
        """
        if days <= 0:
            raise ValidationError("Days must be greater than zero.", field="days")
        if not 0 <= discount <= 1:
            raise ValidationError("Discount must be between 0 and 1.", field="discount")
        if not self._available:
            raise ServiceNotAvailableError(self.name)

        subtotal = self._base_price * days
        after_discount = subtotal * (1 - discount)
        total = after_discount + (self._deposit if include_deposit else 0)
        return round(total, 2)

    def description(self) -> str:
        base = super().description()
        deposit = f"${self._deposit:,.0f}" if self._requires_deposit else "No"
        return f"{base} | Type: {self._equipment_type} | Deposit: {deposit}"


class Consulting(Service):
    """Specialized consulting / advisory service."""

    _LEVEL_MULTIPLIER = {
        "Junior": 1.0,
        "Semi-Senior": 1.3,
        "Senior": 1.6,
        "Expert": 2.0,
    }

    def __init__(
        self,
        name: str,
        base_price: float,
        specialty: str,
        level: str = "Junior",
        available: bool = True,
    ) -> None:
        super().__init__(name, base_price, available)
        if not specialty or not specialty.strip():
            raise ValidationError("Specialty is required.", field="specialty")
        if level not in self._LEVEL_MULTIPLIER:
            raise ValidationError(
                f"Level must be one of {tuple(self._LEVEL_MULTIPLIER)}.",
                field="level",
            )
        self._specialty = specialty.strip()
        self._level = level
        self._multiplier = self._LEVEL_MULTIPLIER[level]
        log_event(f"Consulting registered: {name} ({level})")

    @property
    def specialty(self) -> str:
        return self._specialty

    @property
    def level(self) -> str:
        return self._level

    def calculate_cost(
        self,
        hours: float = 1,
        discount: float = 0.0,
        urgent: bool = False,
    ) -> float:
        """
        Cost = base_price * hours * level_multiplier [* 1.25 if urgent] * (1 - discount)
        """
        if hours <= 0:
            raise ValidationError("Hours must be greater than zero.", field="hours")
        if not 0 <= discount <= 1:
            raise ValidationError("Discount must be between 0 and 1.", field="discount")
        if not self._available:
            raise ServiceNotAvailableError(self.name)

        subtotal = self._base_price * hours * self._multiplier
        if urgent:
            subtotal *= 1.25
        return round(subtotal * (1 - discount), 2)

    def description(self) -> str:
        base = super().description()
        return (
            f"{base} | Specialty: {self._specialty} | "
            f"Level: {self._level} (x{self._multiplier})"
        )
