#!/usr/bin/env python3
"""
================================================================================
  sistema-integral-orientado-a-objetos – Integral Management System
  Clients · Services · Reservations
================================================================================
  UNAD – Programming Course (213023) – Phase 4

  Demonstrates:
  • Abstraction, Inheritance, Polymorphism, Encapsulation
  • Method overloading (optional parameters)
  • Custom exceptions + try/except/else/finally + exception chaining
  • Persistent logging of every event and error
  • ≥ 10 complete operations (valid and invalid)
  • The application never crashes; it continues after every error
================================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the project root importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.system import ManagementSystem
from app.exceptions import SoftwareFJError
from app.utils.logger import log_event, log_exception, LOG_FILE


def separator(title: str = "") -> None:
    print("\n" + "═" * 72)
    if title:
        print(f"  {title}")
        print("═" * 72)


def run_simulations() -> None:
    """Execute at least 12 operations (valid + invalid)."""
    system = ManagementSystem()
    stats = {"success": 0, "controlled_failure": 0}

    separator("SOFTWARE FJ – SIMULATION OF 13 OPERATIONS")
    print("  Valid and invalid operations will be attempted.")
    print("  Every error is caught, logged and does NOT stop the program.\n")

    def op(number: int, title: str):
        print(f"\n▶ OP-{number:02d}  {title}")

    # 1. Valid client
    op(1, "Register valid client (Ana Gómez)")
    try:
        c1 = system.register_client(
            "Ana María Gómez Ríos", "1023456789",
            "ana.gomez@email.com", "3001234567",
        )
        print(f"  ✓ SUCCESS: {c1}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 2. Invalid email
    op(2, "Register client with INVALID email")
    try:
        system.register_client(
            "Andres López", "9876543210", "correo-invalido", "3109876543"
        )
        print("  ✓ SUCCESS (unexpected)")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 3. Second valid client
    op(3, "Register valid client (Carlos Ruiz)")
    try:
        c2 = system.register_client(
            "Carlos Andrés Ruiz Pérez", "1122334455",
            "carlos.ruiz@empresa.com", "3201112233",
        )
        print(f"  ✓ SUCCESS: {c2}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 4. Duplicate document
    op(4, "Register DUPLICATE client (same document)")
    try:
        system.register_client(
            "Ana Duplicada", "1023456789", "otra@email.com", "3000000000"
        )
        print("  ✓ SUCCESS (unexpected)")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 5. Room service
    op(5, "Register Room service")
    try:
        s1 = system.register_room(
            "Sala Ejecutiva Norte", 80_000, capacity=12, has_projector=True
        )
        print(f"  ✓ SUCCESS: {s1}")
        print(f"    {s1.description()}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 6. Equipment service
    op(6, "Register Equipment service")
    try:
        s2 = system.register_equipment(
            "Laptop Dell XPS 15", 45_000, "Computador portátil", requires_deposit=True
        )
        print(f"  ✓ SUCCESS: {s2}")
        print(f"    {s2.description()}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 7. Consulting service
    op(7, "Register Consulting service (Senior)")
    try:
        s3 = system.register_consulting(
            "Asesoría Arquitectura de Software", 120_000,
            specialty="Arquitectura de Software", level="Senior",
        )
        print(f"  ✓ SUCCESS: {s3}")
        print(f"    {s3.description()}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 8. Negative price
    op(8, "Register service with NEGATIVE price")
    try:
        system.register_room("Sala Inválida", -5_000, capacity=5)
        print("  ✓ SUCCESS (unexpected)")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 9. Create + confirm reservation
    op(9, "Create and CONFIRM valid reservation (Room)")
    try:
        r1 = system.create_reservation("1023456789", "Sala Ejecutiva Norte", duration=3)
        print(f"  → Created: {r1}")
        r1.confirm(discount=0.10)
        print(f"  ✓ SUCCESS: Confirmed. Cost = ${r1.calculated_cost:,.0f}")
        print(f"    State: {r1.state}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 10. Confirm already confirmed
    op(10, "Try to CONFIRM an already confirmed reservation")
    try:
        r1.confirm()
        print("  ✓ SUCCESS (unexpected)")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 11. Non-existent client
    op(11, "Create reservation with NON-EXISTENT client")
    try:
        system.create_reservation("0000000000", "Sala Ejecutiva Norte", duration=2)
        print("  ✓ SUCCESS (unexpected)")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 12. Unavailable service
    op(12, "Mark service unavailable and try to confirm")
    try:
        s2.mark_unavailable()
        r2 = system.create_reservation("1122334455", "Laptop Dell XPS 15", duration=2)
        print(f"  → Created (PENDING): {r2}")
        r2.confirm()
        print("  ✓ SUCCESS (unexpected)")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # 13. Bonus – consulting + finish
    op(13, "(Bonus) Confirm consulting reservation and finish it")
    try:
        r3 = system.create_reservation(
            "1023456789", "Asesoría Arquitectura de Software", duration=4
        )
        r3.confirm(discount=0.05, urgent=True)
        print(f"  ✓ Confirmed. Cost = ${r3.calculated_cost:,.0f}")
        r3.finish()
        print(f"  ✓ Finished. Final state = {r3.state}")
        stats["success"] += 1
    except SoftwareFJError as exc:
        print(f"  ✗ CONTROLLED ERROR: {exc}")
        stats["controlled_failure"] += 1

    # Summary
    separator("SIMULATION SUMMARY")
    print(f"  Successful operations       : {stats['success']}")
    print(f"  Controlled failed operations: {stats['controlled_failure']}")
    print(f"  System status               : STABLE (never crashed)")
    print(f"  {system.summary()}")
    print(f"\n  Log file:\n  → {LOG_FILE}")

    separator("REGISTERED CLIENTS")
    for client in system.clients.list_all():
        print(f"  • {client.description()}")

    separator("REGISTERED SERVICES")
    for service in system.services.list_all():
        print(f"  • {service.description()}")

    separator("REGISTERED RESERVATIONS")
    for reservation in system.reservations.list_all():
        print(f"  • {reservation.description()}")

    separator("END OF SIMULATION")
    print("  All required concepts have been demonstrated.")
    print("  Review the log file for the complete event/error history.\n")


if __name__ == "__main__":
    try:
        run_simulations()
    except Exception as exc:  # last-resort safety net
        log_exception(exc, context="main (unexpected)")
        print(f"\n  Unexpected critical error (logged): {exc}")
        print("  The system handled it and will now exit cleanly.\n")
        sys.exit(1)
