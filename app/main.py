"""
Aplicación principal Building Manager Pro
Sistema profesional de gestión de edificios
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Agregar el directorio de la aplicación al path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from ui.views.main_window import MainWindow
from config.settings import Settings

class BuildingManagerApp:
    """Aplicación principal profesional"""
    
    def __init__(self):
        self.settings = Settings()
        self.main_window = None
        
    def run(self):
        """Ejecuta la aplicación"""
        try:
            # Crear y mostrar la ventana principal
            self.main_window = MainWindow()
            self.main_window.run()
            
        except Exception as e:
            self._handle_error(e)
    
    def _handle_error(self, error: Exception):
        """Maneja errores de la aplicación"""
        import tkinter.messagebox as messagebox
        
        error_msg = f"Error en la aplicación:\n{str(error)}"
        messagebox.showerror("Error", error_msg)
        
        # Log del error (en un futuro implementar logging)
        print(f"ERROR: {error}")

def main():
    """Función principal de entrada"""
    app = BuildingManagerApp()
    app.run()

if __name__ == "__main__":
    main() 