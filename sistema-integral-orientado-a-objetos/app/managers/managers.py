"""
In-memory managers (no database).
Each manager owns a private list and exposes a clean API.
"""

from __future__ import annotations

from typing import List, Optional

from app.exceptions import DuplicateError, NotFoundError, ValidationError
from app.models.client import Client
from app.models.service import Service
from app.models.reservation import Reservation
from app.utils.logger import log_event, log_exception


class ClientManager:
    """Manages the collection of clients."""

    def __init__(self) -> None:
        self._clients: List[Client] = []

    def add(self, client: Client) -> Client:
        try:
            if not isinstance(client, Client):
                raise ValidationError("Only Client instances can be added.")
            for existing in self._clients:
                if existing.document == client.document:
                    raise DuplicateError("Client", client.document)
            self._clients.append(client)
            log_event(f"Client registered in manager: {client.name}")
            return client
        except (ValidationError, DuplicateError) as exc:
            log_exception(exc, context="ClientManager.add")
            raise

    def find_by_document(self, document: str) -> Optional[Client]:
        for client in self._clients:
            if client.document == document:
                return client
        return None

    def find_by_id(self, client_id: str) -> Optional[Client]:
        for client in self._clients:
            if client.id == client_id:
                return client
        return None

    def list_all(self) -> List[Client]:
        return list(self._clients)

    def count(self) -> int:
        return len(self._clients)

    def remove(self, document: str) -> bool:
        try:
            for index, client in enumerate(self._clients):
                if client.document == document:
                    removed = self._clients.pop(index)
                    log_event(f"Client removed: {removed.name}")
                    return True
            raise NotFoundError("Client", document)
        except NotFoundError as exc:
            log_exception(exc, context="ClientManager.remove")
            raise


class ServiceManager:
    """Manages the collection of services."""

    def __init__(self) -> None:
        self._services: List[Service] = []

    def add(self, service: Service) -> Service:
        try:
            if not isinstance(service, Service):
                raise ValidationError("Only Service instances can be added.")
            for existing in self._services:
                if existing.name.lower() == service.name.lower():
                    raise DuplicateError("Service", service.name)
            self._services.append(service)
            log_event(f"Service registered in manager: {service.name}")
            return service
        except (ValidationError, DuplicateError) as exc:
            log_exception(exc, context="ServiceManager.add")
            raise

    def find_by_id(self, service_id: str) -> Optional[Service]:
        for service in self._services:
            if service.id == service_id:
                return service
        return None

    def find_by_name(self, name: str) -> Optional[Service]:
        for service in self._services:
            if service.name.lower() == name.lower():
                return service
        return None

    def list_all(self) -> List[Service]:
        return list(self._services)

    def list_available(self) -> List[Service]:
        return [s for s in self._services if s.available]

    def count(self) -> int:
        return len(self._services)


class ReservationManager:
    """Manages the collection of reservations."""

    def __init__(self) -> None:
        self._reservations: List[Reservation] = []

    def add(self, reservation: Reservation) -> Reservation:
        try:
            if not isinstance(reservation, Reservation):
                raise ValidationError("Only Reservation instances can be added.")
            self._reservations.append(reservation)
            log_event(f"Reservation registered in manager: {reservation.id}")
            return reservation
        except ValidationError as exc:
            log_exception(exc, context="ReservationManager.add")
            raise

    def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
        for reservation in self._reservations:
            if reservation.id == reservation_id:
                return reservation
        return None

    def list_all(self) -> List[Reservation]:
        return list(self._reservations)

    def list_by_state(self, state: str) -> List[Reservation]:
        return [r for r in self._reservations if r.state == state.upper()]

    def count(self) -> int:
        return len(self._reservations)
