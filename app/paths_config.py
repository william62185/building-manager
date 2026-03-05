"""
Configuración de rutas portables para Building Manager Pro.
Soporta ejecución normal (desarrollo) y empaquetado con PyInstaller (frozen).
Los datos escritos (JSON, PDFs, etc.) van siempre a una carpeta accesible y escribible.
Cuando está instalado (ej. en Program Files), usa AppData del usuario para evitar
"Acceso denegado" en Windows.
"""

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def _get_base_path() -> Path:
    """Directorio base de la aplicación (datos escribibles)."""
    if getattr(sys, "frozen", False):
        # Ejecutable empaquetado: usar AppData del usuario para que siempre sea escribible
        # (evita "Acceso denegado" si la app está en Program Files)
        appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
        return Path(appdata) / "Building Manager Pro"
    # Desarrollo: raíz del paquete manager (donde están run.py y manager/)
    return Path(__file__).resolve().parent.parent


def _get_manager_root() -> Path:
    """Raíz del paquete manager (código + recursos). En frozen, igual que base."""
    return _get_base_path()


BASE_PATH = _get_base_path()
MANAGER_ROOT = _get_manager_root()

# Carpetas de datos (si no existen, se crean al usarse)
DATA_DIR = BASE_PATH / "data"
BACKUPS_DIR = BASE_PATH / "backups"
DOCUMENTOS_INQUILINOS_DIR = DATA_DIR / "documentos_inquilinos"
GASTOS_DOCS_DIR = BASE_PATH / "gastos_docs"
EXPORTS_DIR = BASE_PATH / "exports"


def get_icon_path() -> Optional[Path]:
    """
    Ruta del icono de la aplicación (.ico).
    En desarrollo: raíz del proyecto / assets / icon.ico.
    En frozen: carpeta del ejecutable / assets / icon.ico (si el instalador incluye assets).
    Devuelve None si el archivo no existe.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
        if base.name == "_internal":
            base = base.parent
    else:
        base = Path(__file__).resolve().parent.parent.parent  # raíz del proyecto
    icon_path = base / "assets" / "icon.ico"
    return icon_path if icon_path.exists() else None


def get_splash_path() -> Optional[Path]:
    """
    Ruta de la imagen de splash (splash.png).
    Misma lógica que get_icon_path: raíz del proyecto / assets en dev, carpeta del ejecutable en frozen.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
        if base.name == "_internal":
            base = base.parent
    else:
        base = Path(__file__).resolve().parent.parent.parent
    splash_path = base / "assets" / "splash.png"
    return splash_path if splash_path.exists() else None


def _sanitize_folder_part(text: str) -> str:
    """Sanitiza una parte del nombre de carpeta (cédula o nombre)."""
    if not text or not str(text).strip():
        return "sin_nombre"
    s = str(text).strip()
    # Reemplazar espacios y caracteres problemáticos por _
    s = re.sub(r'[\s/\\:*?"<>|]+', "_", s)
    s = s.strip("._")
    return s if s else "sin_nombre"


def get_tenant_document_folder_name(tenant: Dict[str, Any]) -> str:
    """
    Devuelve el nombre de la subcarpeta del inquilino en documentos_inquilinos:
    {cedula}_{primer_nombre}, sanitizado (ej: 1223322_william).
    """
    cedula = _sanitize_folder_part(tenant.get("numero_documento") or "")
    nombre_completo = (tenant.get("nombre") or "").strip()
    primer_nombre = nombre_completo.split()[0] if nombre_completo else ""
    nombre = _sanitize_folder_part(primer_nombre)
    return f"{cedula}_{nombre}"


def ensure_dirs():
    """Crea las carpetas de datos si no existen."""
    for d in (DATA_DIR, BACKUPS_DIR, DOCUMENTOS_INQUILINOS_DIR, GASTOS_DOCS_DIR, EXPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
