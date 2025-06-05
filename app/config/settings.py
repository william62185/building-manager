"""
Configuraciones globales de la aplicación
"""

import os
from pathlib import Path

class Settings:
    """Configuraciones de la aplicación"""
    
    # Información de la aplicación
    APP_NAME = "Building Manager"
    APP_VERSION = "1.0.0"
    
    # Base de datos
    DATABASE_PATH = "data/building_manager.db"
    
    # Archivos
    FILES_DIR = Path("files")
    TENANTS_FILES_DIR = FILES_DIR / "tenants"
    DOCUMENTS_DIR = FILES_DIR / "documents"
    EXPORTS_DIR = FILES_DIR / "exports"
    
    # Interfaz
    WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
    WINDOW_SIZE = "1200x800"
    
    # Colores del tema
    COLORS = {
        "primary": "#1e40af",
        "secondary": "#6b7280", 
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6",
        "light": "#f8fafc",
        "dark": "#1f2937",
        "white": "#ffffff",
        "background": "#f8fafc",
        "surface": "#ffffff",
        "border": "#e5e7eb"
    }
    
    # Fuentes
    FONTS = {
        "default": ("Segoe UI", 10),
        "heading": ("Segoe UI", 14, "bold"),
        "title": ("Segoe UI", 16, "bold"),
        "small": ("Segoe UI", 8)
    }
    
    @classmethod
    def get_database_path(cls) -> str:
        """Retorna la ruta completa de la base de datos"""
        return str(Path(cls.DATABASE_PATH).absolute())
    
    @classmethod
    def ensure_directories(cls):
        """Asegura que existan todos los directorios necesarios"""
        directories = [
            cls.FILES_DIR,
            cls.TENANTS_FILES_DIR, 
            cls.DOCUMENTS_DIR,
            cls.EXPORTS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True) 