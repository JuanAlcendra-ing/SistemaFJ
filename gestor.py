"""Sistema de gestión: listas internas y operaciones a prueba de fallos."""
from entidades import Cliente
from excepciones import ClienteInvalidoError, SoftwareFJError
from logger_config import log
from reserva import Reserva


class SistemaGestion:
    def __init__(self, notificar=None):
        self._clientes, self._servicios, self._reservas = [], [], []
        # notificar(exito: bool, mensaje: str): la consola lo imprime, la GUI lo muestra
        self.notificar = notificar or self._notificar_consola

    @staticmethod
    def _notificar_consola(exito, mensaje):
        print(("   ✓ " if exito else "   ✗ ") + mensaje)

    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    def registrar_error(self, descripcion, err):
        """Registra un error SoftwareFJError (o inesperado) en el log y notifica."""
        if isinstance(err, SoftwareFJError):
            causa = f" (causa: {err.__cause__!r})" if err.__cause__ else ""
            log.error("%s -> %s: %s%s", descripcion, type(err).__name__, err, causa)
            self.notificar(False, f"ERROR controlado [{type(err).__name__}]: {err}")
        else:
            log.critical("%s -> Error inesperado %s: %s", descripcion,
                         type(err).__name__, err, exc_info=True)
            self.notificar(False, f"ERROR inesperado [{type(err).__name__}]: {err}")

    def _ejecutar(self, descripcion, funcion):
        """Ejecuta una operación ante cualquier error lo registra y continúa."""
        try:
            resultado = funcion()
        except Exception as err:            # controlado o inesperado: el sistema sigue vivo
            self.registrar_error(descripcion, err)
            return None
        else:
            log.info("%s -> OK", descripcion)
            self.notificar(True, str(resultado))
            return resultado
        finally:
            log.info("Fin de operación: %s", descripcion)

    def registrar_cliente(self, **datos):
        def op():
            cliente = Cliente(**datos)
            if any(c.email == cliente.email or c.documento == cliente.documento
                   for c in self._clientes):
                raise ClienteInvalidoError("Cliente duplicado (email o documento)")
            self._clientes.append(cliente)
            return cliente
        return self._ejecutar("Registrar cliente", op)

    def agregar_servicio(self, clase, *args, **kwargs):
        def op():
            servicio = clase(*args, **kwargs)
            self._servicios.append(servicio)
            return servicio
        return self._ejecutar(f"Crear servicio {clase.__name__}", op)

    def crear_reserva(self, cliente, servicio, duracion):
        def op():
            reserva = Reserva(cliente, servicio, duracion)
            reserva.confirmar()
            self._reservas.append(reserva)
            return reserva
        return self._ejecutar("Crear reserva", op)

    def procesar_reserva(self, reserva, **kwargs):
        return self._ejecutar("Procesar reserva", lambda: f"Costo total: ${reserva.procesar(**kwargs):,.2f}")

    def cancelar_reserva(self, reserva):
        return self._ejecutar("Cancelar reserva", lambda: (reserva.cancelar(), reserva)[1])

    def resumen(self):
        print("\n=== RESUMEN FINAL ===")
        print(f"Clientes: {len(self._clientes)} | Servicios: {len(self._servicios)} "
              f"| Reservas: {len(self._reservas)}")
        for r in self._reservas:
            print("  ", r)
