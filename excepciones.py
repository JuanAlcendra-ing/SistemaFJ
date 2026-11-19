"""Jerarquía de excepciones personalizadas de Software FJ."""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema."""


class DatosInvalidosError(SoftwareFJError):
    """Datos con formato o valor inválido."""


class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio."""


class ClienteInvalidoError(DatosInvalidosError):
    """Datos de cliente inválidos o duplicados."""


class ServicioInvalidoError(DatosInvalidosError):
    """Parámetros de servicio inválidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no está disponible."""


class ReservaError(SoftwareFJError):
    """Error general durante la gestión de una reserva."""


class OperacionNoPermitidaError(ReservaError):
    """Operación no válida para el estado actual de la reserva."""


class CalculoInconsistenteError(SoftwareFJError):
    """Cálculo de costos con valores inconsistentes."""
