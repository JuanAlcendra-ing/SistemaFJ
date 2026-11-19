"""Clase Reserva: integra cliente, servicio, duración y estado."""
from enum import Enum

from entidades import Cliente, EntidadBase
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ParametroFaltanteError, ReservaError,
                         ServicioNoDisponibleError)
from logger_config import log
from servicios import Servicio


class Estado(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    PROCESADA = "Procesada"
    CANCELADA = "Cancelada"


class Reserva(EntidadBase):
    def __init__(self, cliente=None, servicio=None, duracion=None):
        super().__init__()
        if cliente is None or servicio is None or duracion is None:
            raise ParametroFaltanteError("Cliente, servicio y duración son obligatorios")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaError("Tipos inválidos para cliente o servicio")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"'{servicio.nombre}' no está disponible")
        servicio.validar_parametros(duracion)   
        self._cliente, self._servicio, self._duracion = cliente, servicio, duracion
        self._estado = Estado.PENDIENTE
        self._costo = None

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        if self._estado is not Estado.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva {self._estado.value}")
        self._estado = Estado.CONFIRMADA
        log.info("Reserva #%s confirmada", self.id)

    def cancelar(self):
        if self._estado in (Estado.PROCESADA, Estado.CANCELADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self._estado.value}")
        self._estado = Estado.CANCELADA
        log.info("Reserva #%s cancelada", self.id)

    def procesar(self, impuesto=None, descuento=0.0):
        """Calcula el costo final y marca la reserva como procesada."""
        try:
            if self._estado is not Estado.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas confirmadas (estado: {self._estado.value})")
            costo = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
        except (TypeError, ValueError) as err:
            # encadenamiento de excepciones
            raise CalculoInconsistenteError("Fallo en el cálculo de la reserva") from err
        else:
            self._costo = costo
            self._estado = Estado.PROCESADA
            log.info("Reserva #%s procesada. Costo total: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            log.info("Intento de procesamiento finalizado para reserva #%s", self.id)

    def describir(self):
        costo = f"${self._costo:,.2f}" if self._costo is not None else "por calcular"
        return (f"Reserva #{self.id} | {self._cliente.nombre} | {self._servicio.nombre} "
                f"| duración: {self._duracion} | {self._estado.value} | {costo}")
