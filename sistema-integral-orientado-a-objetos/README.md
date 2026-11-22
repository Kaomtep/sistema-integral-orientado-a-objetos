# Sistema Integral Orientado a Objetos

**Universidad Nacional Abierta y a Distancia (UNAD)**  
**Curso:** Programación – Código 213023  
**Fase 4 – Componente práctico (Prácticas simuladas)**  
**Empresa de referencia:** Software FJ

---

## Descripción

Sistema orientado a objetos que gestiona **clientes**, **servicios** (salas, equipos y asesorías) y **reservas** para la empresa Software FJ.

- Sin base de datos (todo en memoria con listas de objetos).
- Manejo robusto de excepciones personalizadas.
- Registro persistente de eventos y errores en archivo de log.
- El sistema **nunca se detiene** ante errores.

---

## Requisitos cumplidos

| Requisito | Implementación |
|-----------|----------------|
| Clase abstracta | `Entity` |
| Cliente con validaciones | `Client` |
| Servicio abstracto + 3 hijas | `Service` → `Room`, `Equipment`, `Consulting` |
| Reserva | `Reservation` (cliente + servicio + duración + estado) |
| Métodos sobrecargados | `calculate_cost(...)` con parámetros opcionales |
| Excepciones personalizadas | Jerarquía completa en `app/exceptions.py` |
| try / except / else / finally | En `Reservation.confirm()` |
| Encadenamiento de excepciones | `raise ... from e` |
| Archivo de logs | `logs.sistema-integral-orientado-a-objetos/.log` |
| ≥ 10 operaciones | 13 operaciones en `main.py` |
| Sistema estable | Ningún error detiene la ejecución |

---

## Estructura del proyecto

```
sistema-integral-orientado-a-objetos/
├── main.py                     # Punto de entrada + simulaciones
├── README.md
├── .gitignore
├── logs/                       # Se genera al ejecutar
│   └── software_fj.log
└── app/
    ├── __init__.py
    ├── exceptions.py           # Excepciones personalizadas
    ├── system.py               # Fachada principal
    ├── models/
    │   ├── __init__.py
    │   ├── base.py             # Clase abstracta Entity
    │   ├── client.py
    │   ├── service.py          # Service + Room + Equipment + Consulting
    │   └── reservation.py
    ├── managers/
    │   ├── __init__.py
    │   └── managers.py         # ClientManager, ServiceManager, ReservationManager
    └── utils/
        ├── __init__.py
        └── logger.py
```

---

## Cómo ejecutar

```bash
cd sistema-integral-orientado-a-objetos
python main.py
```

No se requieren dependencias externas (solo Python 3.10+).

---

## Principios POO demostrados

- **Abstracción** → `Entity`, `Service`
- **Herencia** → `Room`, `Equipment`, `Consulting` heredan de `Service`
- **Polimorfismo** → `calculate_cost()` se comporta distinto según el tipo
- **Encapsulación** → atributos privados + properties con validación
- **Sobrecarga** → parámetros opcionales en `calculate_cost`
- **Manejo avanzado de excepciones** → personalizadas, else, finally, encadenamiento y logging

---

## Autores

Proyecto desarrollado de forma colaborativa en el marco de la Fase 4 del curso de Programación – UNAD.
