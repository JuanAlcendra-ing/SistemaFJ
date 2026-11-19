
from gestor import SistemaGestion
from logger_config import RUTA_LOG, log
from servicios import AlquilerEquipo, Asesoria, ReservaSala

resultados = []          # (numero, exito)
_pendiente = []          # mensajes que el gestor notifica durante la operación actual


def _capturar(exito, mensaje):
    _pendiente.append((exito, mensaje))


def operacion(numero, descripcion, accion):
    """Ejecuta una operación del gestor y muestra si fue válida o error controlado."""
    _pendiente.clear()
    print(f"\n[{numero:02d}] {descripcion}")
    resultado = accion()
    if not _pendiente:      # nunca debería ocurrir: el gestor siempre notifica
        _pendiente.append((resultado is not None, str(resultado)))
    exito, mensaje = _pendiente[-1]
    etiqueta = "VÁLIDA           " if exito else "ERROR CONTROLADO "
    print(f"     -> {etiqueta}| {mensaje}")
    resultados.append((numero, exito))
    return resultado


def main():
    log.info("===== INICIO DE LA SIMULACIÓN POR CONSOLA =====")
    s = SistemaGestion(notificar=_capturar)

    ana = operacion(1, "Registrar cliente válido (Ana Gómez)", lambda: s.registrar_cliente(
        nombre="ana gómez", email="ana@correo.com", telefono="3001234567", documento="1020304050"))
    operacion(2, "Registrar cliente con email inválido", lambda: s.registrar_cliente(
        nombre="Pedro Ruiz", email="pedro#correo", telefono="3001112222", documento="99887766"))
    luis = operacion(3, "Registrar cliente válido (Luis Pérez)", lambda: s.registrar_cliente(
        nombre="Luis Pérez", email="luis@correo.com", telefono="+573105556677", documento="80123456"))
    operacion(4, "Registrar cliente duplicado (mismo email y documento)", lambda: s.registrar_cliente(
        nombre="Ana Gómez", email="ana@correo.com", telefono="3001234567", documento="1020304050"))
    operacion(5, "Registrar cliente sin teléfono (parámetro faltante)", lambda: s.registrar_cliente(
        nombre="Sin Telefono", email="sin@correo.com", documento="12345678"))

    sala = operacion(6, "Crear servicio ReservaSala válido",
                     lambda: s.agregar_servicio(ReservaSala, "Sala Innovación", 50000, 12))
    operacion(7, "Crear ReservaSala con capacidad negativa",
              lambda: s.agregar_servicio(ReservaSala, "Sala Fantasma", 40000, -5))
    equipo = operacion(8, "Crear AlquilerEquipo válido",
                       lambda: s.agregar_servicio(AlquilerEquipo, "Portátil Pro", 30000, deposito=100000))
    ase = operacion(9, "Crear Asesoría válida (nivel senior)",
                    lambda: s.agregar_servicio(Asesoria, "Asesoría Cloud", 80000, "Cloud", "senior"))
    operacion(10, "Crear Asesoría con nivel inválido",
              lambda: s.agregar_servicio(Asesoria, "Asesoría X", 80000, "IA", "gurú"))

    r1 = operacion(11, "Crear reserva válida (Ana, sala, 5 horas)",
                   lambda: s.crear_reserva(ana, sala, 5))
    operacion(12, "Crear reserva con duración fuera de rango (20 horas)",
              lambda: s.crear_reserva(luis, sala, 20))
    operacion(13, "Crear reserva sin cliente (parámetro faltante)",
              lambda: s.crear_reserva(None, sala, 2))
    operacion(14, "Procesar reserva #1 con IVA por defecto (19 %)",
              lambda: s.procesar_reserva(r1))
    operacion(15, "Cancelar reserva ya procesada (operación no permitida)",
              lambda: s.cancelar_reserva(r1))

    equipo.disponible = False
    operacion(16, "Reservar un equipo marcado como no disponible",
              lambda: s.crear_reserva(luis, equipo, 3))
    equipo.disponible = True

    r2 = operacion(17, "Crear reserva válida (Luis, asesoría, 2 horas)",
                   lambda: s.crear_reserva(luis, ase, 2))
    operacion(18, "Procesar con descuento inconsistente (80 %)",
              lambda: s.procesar_reserva(r2, descuento=0.8))
    operacion(19, "Reintentar procesar sin impuesto y con 10 % de descuento",
              lambda: s.procesar_reserva(r2, impuesto=0.0, descuento=0.10))
    r3 = operacion(20, "Crear reserva válida (Ana, equipo, 4 días)",
                   lambda: s.crear_reserva(ana, equipo, 4))
    operacion(21, "Cancelar la reserva anterior", lambda: s.cancelar_reserva(r3))
    operacion(22, "Procesar una reserva cancelada (operación no permitida)",
              lambda: s.procesar_reserva(r3))

    validas = sum(1 for _, ok in resultados if ok)
    errores = len(resultados) - validas
    print("\n" + "=" * 60)
    print(f"Operaciones: {len(resultados)} | Válidas: {validas} | Errores controlados: {errores}")
    print("Errores controlados en las operaciones:",
          ", ".join(f"{n:02d}" for n, ok in resultados if not ok))
    s.resumen()
    print(f"\nEl programa terminó sin interrupciones. Log: {RUTA_LOG}")
    log.info("===== FIN DE LA SIMULACIÓN POR CONSOLA =====")


if __name__ == "__main__":
    main()