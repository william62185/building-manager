"""
Helpers de persistencia segura para Building Manager Pro.
Escritura atómica para evitar corrupción de JSON si la app se cierra a mitad de escritura.
"""

import json
import os
from pathlib import Path
from typing import Any, Union

from manager.app.logger import logger


def save_json_atomic(
    path: Union[Path, str],
    data: Any,
    encoding: str = "utf-8",
    ensure_ascii: bool = False,
    indent: int = 2,
) -> bool:
    """
    Escribe data como JSON de forma atómica (temp + replace).
    Reduce el riesgo de corrupción si la aplicación se cierra durante la escritura.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + ".tmp")
    try:
        with open(tmp, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
        os.replace(tmp, path)
        return True
    except Exception as e:
        logger.exception("Error en escritura atómica de %s: %s", path, e)
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass
        return False
