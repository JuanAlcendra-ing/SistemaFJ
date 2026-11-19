"""Entidad abstracta general y clase Cliente (con encapsulación y validaciones)."""
import re
from abc import ABC, abstractmethod
from itertools import count

from excepciones import ClienteInvalidoError, ParametroFaltanteError


class EntidadBase(ABC):
    """Clase abstracta que representa cualquier entidad del sistema."""

    _contador = count(1)

    def __init__(self):
        self._id = next(EntidadBase._contador)

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""

    def __str__(self):
        return self.describir()


class Cliente(EntidadBase):
    """Cliente con datos personales encapsulados y validados."""

    _RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
    _RE_TEL = re.compile(r"^\+?\d{7,15}$")
    _RE_DOC = re.compile(r"^\d{5,12}$")

    def __init__(self, nombre=None, email=None, telefono=None, documento=None):
        super().__init__()
        for campo, valor in (("nombre", nombre), ("email", email),
                             ("telefono", telefono), ("documento", documento)):
            if valor is None:
                raise ParametroFaltanteError(f"Falta el parámetro '{campo}' del cliente")
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.__documento = None
        self.documento = documento          # atributo privado con validación

    # --- propiedades con validación ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3 \
                or any(ch.isdigit() for ch in valor):
            raise ClienteInvalidoError(f"Nombre inválido: {valor!r}")
        self._nombre = valor.strip().title()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not self._RE_EMAIL.match(valor.strip()):
            raise ClienteInvalidoError(f"Email inválido: {valor!r}")
        self._email = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not isinstance(valor, str) or not self._RE_TEL.match(valor.strip()):
            raise ClienteInvalidoError(f"Teléfono inválido: {valor!r}")
        self._telefono = valor.strip()

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        if not isinstance(valor, str) or not self._RE_DOC.match(valor.strip()):
            raise ClienteInvalidoError(f"Documento inválido: {valor!r}")
        self.__documento = valor.strip()

    def describir(self) -> str:
        return f"Cliente #{self.id}: {self.nombre} <{self.email}> Tel: {self.telefono}"
