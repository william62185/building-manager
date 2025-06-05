"""
Punto de entrada principal de la aplicación
"""

import tkinter as tk
import logging
import sys
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('building_manager.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Configura el entorno de la aplicación"""
    # Crear directorios necesarios
    directories = [
        'data',
        'files',
        'files/tenants',
        'files/documents',
        'files/exports',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("Entorno configurado correctamente")

def main():
    """Función principal de la aplicación"""
    try:
        logger.info("Iniciando Building Manager v1.0.0")
        
        # Configurar entorno
        setup_environment()
        
        # Importar y crear ventana principal
        from ui.main_window import MainWindow
        
        # Crear aplicación
        app = MainWindow()
        
        logger.info("Aplicación iniciada exitosamente")
        
        # Ejecutar loop principal
        app.run()
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        raise

if __name__ == "__main__":
    main() 