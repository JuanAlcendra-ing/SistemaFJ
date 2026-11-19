"""Configuración del archivo de logs (eventos y errores)."""
import logging
from pathlib import Path

RUTA_LOG = Path(__file__).resolve().parent / "logs" / "sistema.log"


def obtener_logger() -> logging.Logger:
    logger = logging.getLogger("software_fj")
    if logger.handlers:         
        return logger
    logger.setLevel(logging.INFO)
    RUTA_LOG.parent.mkdir(exist_ok=True)
    handler = logging.FileHandler(RUTA_LOG, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"))
    logger.addHandler(handler)
    return logger


log = obtener_logger()
