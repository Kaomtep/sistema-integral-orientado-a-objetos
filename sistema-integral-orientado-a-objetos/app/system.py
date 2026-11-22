"""
System facade – single entry point for all business operations.
"""

from __future__ import annotations

from app.exceptions import NotFoundError
from app.managers import ClientManager, ServiceManager, ReservationManager
from app.models import Client, Room, Equipment, Consulting, Reservation
from app.utils.logger import log_event


class ManagementSystem:
    """
    Orchestrates clients, services and reservations.
    Keeps the interface layer free of low-level details.
    """

    def __init__(self) -> None:
        self.clients = ClientManager()
        self.services = ServiceManager()
        self.reservations = ReservationManager()
        log_event("sistema-integral-orientado-a-objetos Management System started.")

    # ------------------------------------------------------------------
    # Clients
    # ------------------------------------------------------------------
    def register_client(
        self,
        name: str,
        document: str,
        email: str,
        phone: str = "",
    ) -> Client:
        client = Client(name, document, email, phone)
        return self.clients.add(client)

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------
    def register_room(
        self,
        name: str,
        base_price: float,
        capacity: int,
        has_projector: bool = False,
    ) -> Room:
        room = Room(name, base_price, capacity, has_projector)
        return self.services.add(room)

    def register_equipment(
        self,
        name: str,
        base_price: float,
        equipment_type: str,
        requires_deposit: bool = True,
    ) -> Equipment:
        equipment = Equipment(name, base_price, equipment_type, requires_deposit)
        return self.services.add(equipment)

    def register_consulting(
        self,
        name: str,
        base_price: float,
        specialty: str,
        level: str = "Junior",
    ) -> Consulting:
        consulting = Consulting(name, base_price, specialty, level)
        return self.services.add(consulting)

    # ------------------------------------------------------------------
    # Reservations
    # ------------------------------------------------------------------
    def create_reservation(
        self,
        client_document: str,
        service_name: str,
        duration: float,
        notes: str = "",
    ) -> Reservation:
        client = self.clients.find_by_document(client_document)
        if client is None:
            raise NotFoundError("Client", client_document)

        service = self.services.find_by_name(service_name)
        if service is None:
            raise NotFoundError("Service", service_name)

        reservation = Reservation(client, service, duration, notes)
        return self.reservations.add(reservation)

    def summary(self) -> str:
        return (
            f"Clients: {self.clients.count()} | "
            f"Services: {self.services.count()} | "
            f"Reservations: {self.reservations.count()}"
        )
