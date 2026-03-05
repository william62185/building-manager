"""
Logging centralizado para Building Manager Pro.
En producción no se usan prints de diagnóstico; todo pasa por este módulo.
"""

import logging
import sys

# Logger de la aplicación
logger = logging.getLogger("building_manager")

# Evitar duplicar handlers si se reconfigura
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


def set_level(level: str) -> None:
    """Establece el nivel (DEBUG, INFO, WARNING, ERROR)."""
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
