#!/usr/bin/env python3
"""
Script para construir el instalador de Building Manager Pro.
Genera un ejecutable con PyInstaller y opcionalmente un instalador Windows con Inno Setup.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "BuildingManagerPro.spec"


def run(cmd: list, cwd: Path = PROJECT_ROOT) -> bool:
    """Ejecuta un comando y retorna True si tuvo éxito."""
    print(f"  $ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd)
    return r.returncode == 0


def main():
    print("Building Manager Pro - Build del instalador\n")

    # 1. Instalar dependencias de build si hace falta
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        if not run([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"]):
            print("Error al instalar PyInstaller.")
            return 1
        print()

    # 2. Ejecutar PyInstaller
    print("Ejecutando PyInstaller...")
    if not run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(SPEC_FILE)]):
        print("Error al ejecutar PyInstaller.")
        return 1

    app_dir = DIST_DIR / "Building Manager Pro"
    exe_path = app_dir / "Building Manager Pro.exe"
    if not exe_path.exists():
        print("No se encontró el ejecutable generado.")
        return 1

    print(f"\nListo. Aplicación empaquetada en:\n  {app_dir}\n")
    print("Para probar en local:")
    print(f"  1. Abre la carpeta: {app_dir}")
    print("  2. Ejecuta 'Building Manager Pro.exe'")
    print("  3. Los datos (JSON, PDFs, etc.) se crearán en esa misma carpeta (data, recibos, exports, etc.).\n")

    # 3. Inno Setup (opcional)
    inno_paths = [
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Inno Setup 6" / "ISCC.exe",
    ]
    iss_file = PROJECT_ROOT / "installer" / "BuildingManagerPro.iss"
    if iss_file.exists():
        for iscc in inno_paths:
            if iscc.exists():
                print("Creando instalador Windows con Inno Setup...")
                if run([str(iscc), str(iss_file)], cwd=PROJECT_ROOT):
                    print("Instalador creado en dist/")
                break
        else:
            print("Inno Setup no encontrado. Instala Inno Setup 6 para generar el .exe instalador.")
    else:
        print("Para generar un instalador .exe (Inno Setup), crea installer/BuildingManagerPro.iss")

    return 0


if __name__ == "__main__":
    sys.exit(main())
