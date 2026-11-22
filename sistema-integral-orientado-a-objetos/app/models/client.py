"""
Client entity with strict validation and encapsulation.
"""

from __future__ import annotations

import re

from app.exceptions import ValidationError
from app.models.base import Entity
from app.utils.logger import log_event, log_exception


class Client(Entity):
    """
    Represents a customer of sistema-integral-orientado-a-objetos/

    All personal data is encapsulated behind properties that
    enforce format and presence rules.
    """

    _EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __init__(
        self,
        name: str,
        document: str,
        email: str,
        phone: str = "",
    ) -> None:
        super().__init__(name)
        self._document: str = ""
        self._email: str = ""
        self._phone: str = ""

        self.document = document
        self.email = email
        self.phone = phone

        try:
            self.validate()
            log_event(f"Client created: {self.name} (doc={self.document})")
        except ValidationError as exc:
            log_exception(exc, context="Client.__init__")
            raise

    # ------------------------------------------------------------------
    # Properties with validation
    # ------------------------------------------------------------------
    @property
    def document(self) -> str:
        return self._document

    @document.setter
    def document(self, value: str) -> None:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise ValidationError("Document number is required.", field="document")
        if not cleaned.isdigit() or len(cleaned) < 6:
            raise ValidationError(
                "Document must contain only digits and be at least 6 characters.",
                field="document",
            )
        self._document = cleaned

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise ValidationError("Email is required.", field="email")
        if not self._EMAIL_PATTERN.match(cleaned):
            raise ValidationError("Invalid email format.", field="email")
        self._email = cleaned.lower()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not value or not str(value).strip():
            self._phone = ""
            return
        cleaned = re.sub(r"[\s\-\(\)]", "", str(value))
        if not cleaned.isdigit() or len(cleaned) < 7:
            raise ValidationError(
                "Phone must contain only digits and be at least 7 characters.",
                field="phone",
            )
        self._phone = cleaned

    # ------------------------------------------------------------------
    # Contract implementation
    # ------------------------------------------------------------------
    def validate(self) -> bool:
        if not self._name:
            raise ValidationError("Client name is required.", field="name")
        if not self._document:
            raise ValidationError("Client document is required.", field="document")
        if not self._email:
            raise ValidationError("Client email is required.", field="email")
        return True

    def description(self) -> str:
        phone = self._phone or "N/A"
        return (
            f"Client [{self.id}] {self.name} | "
            f"Doc: {self.document} | Email: {self.email} | Phone: {phone}"
        )

    def __str__(self) -> str:
        return f"Client({self.name}, doc={self.document})"
