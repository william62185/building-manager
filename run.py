#!/usr/bin/env python3
"""
Building Manager Pro - Lanzador principal
Sistema profesional de gestión de edificios
"""

import sys
from pathlib import Path

# En modo empaquetado (PyInstaller), sys.frozen está definido
if getattr(sys, 'frozen', False):
    # Ejecutable empaquetado: usar el directorio del ejecutable
    _root = Path(sys.executable).resolve().parent
    # Si estamos en _internal, subir un nivel
    if _root.name == "_internal":
        _root = _root.parent
else:
    # Desarrollo: raíz del proyecto (donde están run.py y manager/)
    _root = Path(__file__).resolve().parent

# Agregar raíz al path si no está
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Importar paths_config primero y crear directorios antes de cualquier otro código de manager
try:
    import manager.app.paths_config as _paths_cfg
except ImportError:
    manager_path = _root / "manager"
    if manager_path.exists() and str(manager_path.parent) not in sys.path:
        sys.path.insert(0, str(manager_path.parent))
    import manager.app.paths_config as _paths_cfg
if hasattr(_paths_cfg, "ensure_dirs"):
    try:
        _paths_cfg.ensure_dirs()
    except Exception:
        pass

from manager.app.main import main

if __name__ == "__main__":
    main() 