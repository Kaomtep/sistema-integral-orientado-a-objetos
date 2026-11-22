"""
Abstract base entity for all domain objects in Software FJ.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from app.exceptions import ValidationError


class Entity(ABC):
    """
    Abstract root of the domain model.

    Provides a unique identifier, creation timestamp and
    a common activation flag. Subclasses must implement
    `validate()` and `description()`.
    """

    def __init__(self, name: str = "") -> None:
        self._id: str = str(uuid.uuid4())[:8].upper()
        self._name: str = ""
        self._created_at: datetime = datetime.now()
        self._active: bool = True
        if name:
            self.name = name  # goes through the setter

    # ------------------------------------------------------------------
    # Encapsulation
    # ------------------------------------------------------------------
    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not str(value).strip():
            raise ValidationError("Name cannot be empty.", field="name")
        self._name = str(value).strip()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def active(self) -> bool:
        return self._active

    def deactivate(self) -> None:
        self._active = False

    def activate(self) -> None:
        self._active = True

    # ------------------------------------------------------------------
    # Abstract contract
    # ------------------------------------------------------------------
    @abstractmethod
    def validate(self) -> bool:
        """Return True if the entity is valid; raise ValidationError otherwise."""

    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of the entity."""

    def __str__(self) -> str:
        return f"[{self._id}] {self._name}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, name={self._name!r})"
