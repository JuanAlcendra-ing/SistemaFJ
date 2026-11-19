"""Clase abstracta Servicio y tres servicios especializados."""
from abc import ABC, abstractmethod

from entidades import EntidadBase
from excepciones import CalculoInconsistenteError, ServicioInvalidoError

IVA_DEFECTO = 0.19


class Servicio(EntidadBase, ABC):
    """Servicio genérico: define el contrato polimórfico."""

    def __init__(self, nombre, tarifa_base, disponible=True):
        super().__init__()
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El nombre del servicio es obligatorio")
        if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool) \
                or tarifa_base <= 0:
            raise ServicioInvalidoError(f"Tarifa base inválida: {tarifa_base!r}")
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)

    # --- métodos abstractos (se sobrescriben en cada servicio) ---
    @abstractmethod
    def calcular_costo_base(self, duracion) -> float:
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, duracion) -> None:
        """Lanza ServicioInvalidoError si la duración no es válida."""

    # --- método "sobrecargado" mediante parámetros opcionales ---
    def calcular_costo(self, duracion, impuesto=None, descuento=0.0) -> float:
        """Variantes:
        calcular_costo(d)                      -> con IVA por defecto (19 %)
        calcular_costo(d, impuesto=0.0)        -> sin impuesto
        calcular_costo(d, impuesto=0.1)        -> impuesto personalizado
        calcular_costo(d, descuento=0.15)      -> con descuento + IVA por defecto
        """
        impuesto = IVA_DEFECTO if impuesto is None else impuesto
        if not 0 <= impuesto <= 0.5:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango: {impuesto}")
        if not 0 <= descuento <= 0.5:
            raise CalculoInconsistenteError(f"Descuento fuera de rango: {descuento}")
        self.validar_parametros(duracion)
        total = self.calcular_costo_base(duracion) * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo calculado es no positivo")
        return round(total, 2)

    def describir(self) -> str:
        estado = "disponible" if self._disponible else "NO disponible"
        return f"{self.__class__.__name__} #{self.id} '{self.nombre}' ({estado})"


def _validar_entero(valor, minimo, maximo, unidad):
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ServicioInvalidoError(f"La duración debe ser un entero de {unidad}: {valor!r}")
    if not minimo <= valor <= maximo:
        raise ServicioInvalidoError(
            f"Duración fuera de rango ({minimo}-{maximo} {unidad}): {valor}")


class ReservaSala(Servicio):
    """Reserva de sala por horas (1-8). Descuento por volumen >= 4 horas."""

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad

    def validar_parametros(self, duracion):
        _validar_entero(duracion, 1, 8, "horas")

    def calcular_costo_base(self, duracion):
        base = self._tarifa_base * duracion
        return base * 0.90 if duracion >= 4 else base

    def describir(self):
        return f"{super().describir()} - Sala para {self._capacidad} personas, ${self._tarifa_base:,.0f}/hora"


class AlquilerEquipo(Servicio):
    """Alquiler de equipo por días (1-30) más un depósito fijo."""

    def __init__(self, nombre, tarifa_dia, deposito=0, disponible=True):
        super().__init__(nombre, tarifa_dia, disponible)
        if not isinstance(deposito, (int, float)) or deposito < 0:
            raise ServicioInvalidoError(f"Depósito inválido: {deposito!r}")
        self._deposito = float(deposito)

    def validar_parametros(self, duracion):
        _validar_entero(duracion, 1, 30, "días")

    def calcular_costo_base(self, duracion):
        return self._tarifa_base * duracion + self._deposito

    def describir(self):
        return f"{super().describir()} - Equipo, ${self._tarifa_base:,.0f}/día + depósito ${self._deposito:,.0f}"


class Asesoria(Servicio):
    """Asesoría especializada por horas (1-6) el nivel multiplica la tarifa."""

    _NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La especialidad es obligatoria")
        if nivel not in self._NIVELES:
            raise ServicioInvalidoError(
                f"Nivel inválido {nivel!r} use {list(self._NIVELES)}")
        self._especialidad = especialidad.strip()
        self._nivel = nivel

    def validar_parametros(self, duracion):
        _validar_entero(duracion, 1, 6, "horas")

    def calcular_costo_base(self, duracion):
        return self._tarifa_base * self._NIVELES[self._nivel] * duracion

    def describir(self):
        return f"{super().describir()} - Asesoría en {self._especialidad} (nivel {self._nivel})"
