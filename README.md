# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto en **Python 3.8+**, sin librerías externas ni bases de datos.
Ejecución: `python main.py` (genera `logs/sistema.log`).

## Estructura
| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y derivadas) |
| `logger_config.py` | Logger a archivo (único uso de archivos: eventos y errores) |
| `entidades.py` | `EntidadBase` (abstracta) y `Cliente` (encapsulación + validaciones) |
| `servicios.py` | `Servicio` (abstracta), `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | `Reserva` + `Estado`: confirmar, cancelar, procesar |
| `gestor.py` | `SistemaGestion`: listas internas y ejecución a prueba de fallos |
| `main.py` | Simulación de 14 operaciones válidas e inválidas |

## Conceptos aplicados
- **Abstracción**: `EntidadBase` y `Servicio` (métodos `@abstractmethod`).
- **Herencia / polimorfismo**: cada servicio sobrescribe `calcular_costo_base`, `validar_parametros` y `describir`.
- **Encapsulación**: atributos privados/protegidos con `@property` y validación en los setters.
- **Sobrecarga**: `calcular_costo(duracion, impuesto=None, descuento=0.0)` admite varias variantes.
- **Excepciones**: personalizadas; `try/except/else/finally` en `Reserva.procesar` y `SistemaGestion._ejecutar`;
  encadenamiento con `raise ... from err`; todo error se registra en el log y el programa continúa.

## Reparto sugerido (5 integrantes)
1. Excepciones y logger · 2. Cliente y entidad base · 3. Servicios · 4. Reserva y estados · 5. Gestor, main y documentación.
