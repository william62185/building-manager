#!/usr/bin/env python3
"""
Script de migración para convertir el proyecto monolítico 
a estructura modular para Cursor IDE
"""

import os
import shutil
from pathlib import Path


def create_directory_structure():
    """Crea la estructura de directorios del proyecto"""
    directories = [
        "src",
        "src/modules",
        "src/utils", 
        "src/ui",
        "data",
        "data/backups",
        "docs",
        "assets",
        "assets/icons",
        "assets/templates",
        "tests",
        "migrations"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Crear __init__.py en directorios de Python
        if any(python_dir in directory for python_dir in ["src", "modules", "utils", "ui", "tests"]):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Estructura de directorios creada")


def migrate_existing_files():
    """Migra archivos existentes a la nueva estructura"""
    file_migrations = {
        # Archivos existentes -> Nueva ubicación
        "edificio_app_fixed.py": "src/main.py",
        "migrar_inquilinos.py": "migrations/002_add_tenant_fields.py",
        "migrar_archivos.py": "migrations/003_add_file_attachments.py",
        "README.md": "docs/README.md",
        ".gitignore": ".gitignore",  # Se mantiene en raíz
        "edificio.db": "data/edificio.db"
    }
    
    for source, destination in file_migrations.items():
        if os.path.exists(source):
            # Crear directorio destino si no existe
            dest_dir = Path(destination).parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo
            shutil.copy2(source, destination)
            print(f"✅ Migrado: {source} -> {destination}")
        else:
            print(f"⚠️  No encontrado: {source}")


def create_config_files():
    """Crea archivos de configuración necesarios"""
    
    # run.py - Script principal de ejecución
    run_py = """#!/usr/bin/env python3
\"\"\"
Script principal para ejecutar Building Manager
\"\"\"

import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from main import main

if __name__ == "__main__":
    main()
"""
    
    with open("run.py", "w", encoding="utf-8") as f:
        f.write(run_py)
    
    # build.py - Script para crear ejecutable
    build_py = """#!/usr/bin/env python3
\"\"\"
Script para crear ejecutable con PyInstaller
\"\"\"

import subprocess
import sys
from pathlib import Path

def build_executable():
    \"\"\"Crea ejecutable usando PyInstaller\"\"\"
    
    # Configuración de PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=BuildingManager",
        "--add-data=data;data",
        "--add-data=assets;assets",
        "--icon=assets/icons/app.ico",  # Si tienes icono
        "run.py"
    ]
    
    print("🔨 Creando ejecutable...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ Ejecutable creado en dist/BuildingManager.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando ejecutable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
"""
    
    with open("build.py", "w", encoding="utf-8") as f:
        f.write(build_py)
    
    print("✅ Scripts de configuración creados")


def create_vscode_settings():
    """Crea configuración para VS Code/Cursor"""
    
    # Crear directorio .vscode
    Path(".vscode").mkdir(exist_ok=True)
    
    # settings.json
    settings = """{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "dist/": true,
        "build/": true,
        "*.egg-info/": true
    }
}"""
    
    with open(".vscode/settings.json", "w") as f:
        f.write(settings)
    
    # launch.json para debugging
    launch = """{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Building Manager",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Building Manager (Debug)",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "args": ["--debug"]
        }
    ]
}"""
    
    with open(".vscode/launch.json", "w") as f:
        f.write(launch)
    
    print("✅ Configuración de Cursor/VS Code creada")


def main():
    """Función principal de migración"""
    print("🚀 Iniciando migración a Cursor IDE...")
    print("=" * 50)
    
    # Crear estructura
    create_directory_structure()
    
    # Migrar archivos existentes
    migrate_existing_files()
    
    # Crear scripts de configuración
    create_config_files()
    
    # Crear configuración de Cursor/VS Code
    create_vscode_settings()
    
    print("\n" + "=" * 50)
    print("✅ ¡Migración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Abrir el proyecto en Cursor IDE")
    print("2. Crear entorno virtual: python -m venv venv")
    print("3. Activar entorno: venv\\Scripts\\activate (Windows)")
    print("4. Instalar dependencias: pip install -r requirements.txt")
    print("5. Ejecutar aplicación: python run.py")
    print("\n🎯 El código ahora está modularizado y listo para Cursor!")


if __name__ == "__main__":
    main()