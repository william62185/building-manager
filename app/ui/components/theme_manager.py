"""
Theme Manager para Building Manager Pro
Sistema de temas y estilos para la aplicación
"""

import tkinter as tk
from typing import Dict, Any


class Spacing:
    """Constantes de espaciado para la UI"""
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


class Colors:
    """Constantes de colores para la aplicación"""
    # Colores principales
    PRIMARY = "#2563eb"  # Azul
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#3b82f6"
    
    # Colores de estado
    SUCCESS = "#10b981"  # Verde
    WARNING = "#f59e0b"  # Amarillo
    ERROR = "#ef4444"    # Rojo
    INFO = "#3b82f6"     # Azul info
    
    # Colores de texto
    TEXT_PRIMARY = "#1f2937"
    TEXT_SECONDARY = "#6b7280"
    TEXT_ACCENT = "#2563eb"
    TEXT_LIGHT = "#9ca3af"
    
    # Colores de fondo
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f9fafb"
    BG_TERTIARY = "#f3f4f6"
    
    # Colores de borde
    BORDER_LIGHT = "#e5e7eb"
    BORDER_MEDIUM = "#d1d5db"
    BORDER_DARK = "#9ca3af"


class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                # Fondos
                "bg_primary": Colors.BG_PRIMARY,
                "bg_secondary": Colors.BG_SECONDARY,
                "bg_tertiary": Colors.BG_TERTIARY,
                
                # Textos
                "text_primary": Colors.TEXT_PRIMARY,
                "text_secondary": Colors.TEXT_SECONDARY,
                "text_accent": Colors.TEXT_ACCENT,
                "text_light": Colors.TEXT_LIGHT,
                
                # Botones primarios
                "btn_primary_bg": Colors.PRIMARY,
                "btn_primary_fg": "#ffffff",
                "btn_primary_hover": Colors.PRIMARY_DARK,
                
                # Botones secundarios
                "btn_secondary_bg": Colors.BG_SECONDARY,
                "btn_secondary_fg": Colors.TEXT_PRIMARY,
                "btn_secondary_hover": Colors.BG_TERTIARY,
                
                # Bordes
                "border_light": Colors.BORDER_LIGHT,
                "border_medium": Colors.BORDER_MEDIUM,
                "border_dark": Colors.BORDER_DARK,
                
                # Acento
                "bg_accent": Colors.PRIMARY_LIGHT,
                
                # Estados
                "success": Colors.SUCCESS,
                "warning": Colors.WARNING,
                "error": Colors.ERROR,
                "info": Colors.INFO,
            }
        }
    
    def get_style(self, style_name: str) -> Dict[str, Any]:
        """Obtiene un estilo predefinido"""
        theme = self.themes[self.current_theme]
        
        styles = {
            "window": {
                "bg": theme["bg_primary"]
            },
            "frame": {
                "bg": theme["bg_primary"]
            },
            "label_title": {
                "bg": theme["bg_primary"],
                "fg": theme["text_primary"],
                "font": ("Segoe UI", 16, "bold")
            },
            "label_body": {
                "bg": theme["bg_primary"],
                "fg": theme["text_primary"],
                "font": ("Segoe UI", 11)
            },
            "label_secondary": {
                "bg": theme["bg_primary"],
                "fg": theme["text_secondary"],
                "font": ("Segoe UI", 10)
            },
            "card": {
                "bg": theme["bg_primary"],
                "relief": "flat",
                "bd": 1
            },
            "button_primary": {
                "bg": theme["btn_primary_bg"],
                "fg": theme["btn_primary_fg"],
                "relief": "flat",
                "bd": 0,
                "cursor": "hand2",
                "font": ("Segoe UI", 11, "bold")
            },
            "button_secondary": {
                "bg": theme["btn_secondary_bg"],
                "fg": theme["btn_secondary_fg"],
                "relief": "flat",
                "bd": 1,
                "cursor": "hand2",
                "font": ("Segoe UI", 11)
            }
        }
        
        return styles.get(style_name, {})
    
    def set_theme(self, theme_name: str):
        """Cambia el tema actual"""
        if theme_name in self.themes:
            self.current_theme = theme_name


# Instancia global del gestor de temas
theme_manager = ThemeManager()

