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
        # Tema fijo en claro (sin selector de apariencia ni modo oscuro)
        self.current_theme = "light"
        self.themes = {
            "light": {
                # Fondos
                "bg_primary": Colors.BG_PRIMARY,
                "bg_secondary": Colors.BG_SECONDARY,
                "bg_tertiary": Colors.BG_TERTIARY,
                # Menú lateral: azul oscuro (no modificar; se mantiene como estaba)
                "sidebar_bg": "#1e3a5f",
                "sidebar_hover": "#2d4a6f",
                "sidebar_fg": "#ffffff",
                "sidebar_fg_secondary": "#94a3b8",
                "content_bg": "#d0ca98",   # oliva más vivo (misma fuerza que el título, sin palidez)
                "header_bg": "#b86a5c",    # terracotta con misma viveza/saturación que el navy del menú
                
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
    
    def apply_theme_to_widget(self, widget, theme_name: str = None):
        """Aplica el tema a un widget y sus hijos recursivamente"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name not in self.themes:
            return
        
        theme = self.themes[theme_name]
        
        try:
            if not widget.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            return
        
        try:
            # Aplicar tema según el tipo de widget
            widget_type = widget.winfo_class()
            
            # Colores de tema light y dark para comparación
            light_colors = {
                "bg": [Colors.BG_PRIMARY, Colors.BG_SECONDARY, Colors.BG_TERTIARY, "#ffffff", "#f9fafb", "#f3f4f6"],
                "fg": [Colors.TEXT_PRIMARY, Colors.TEXT_SECONDARY, Colors.TEXT_LIGHT, "#1f2937", "#6b7280", "#9ca3af"]
            }
            dark_colors = {
                "bg": ["#1f2937", "#111827", "#374151"],
                "fg": ["#f9fafb", "#d1d5db", "#9ca3af"]
            }
            
            if widget_type in ["Frame", "Toplevel", "Tk"]:
                current_bg = widget.cget("bg")
                # Determinar qué color de fondo usar basado en el color actual
                if current_bg in [Colors.BG_SECONDARY, "#f9fafb", "#111827"]:
                    # Es un sidebar o elemento con bg_secondary
                    widget.configure(bg=theme["bg_secondary"])
                elif current_bg in [Colors.BG_TERTIARY, "#f3f4f6", "#374151"]:
                    # Es un elemento con bg_tertiary
                    widget.configure(bg=theme["bg_tertiary"])
                else:
                    # Por defecto usar bg_primary
                    widget.configure(bg=theme["bg_primary"])
            elif widget_type == "Label":
                try:
                    current_bg = widget.cget("bg")
                    current_fg = widget.cget("fg")
                    
                    # Determinar qué color de fondo usar
                    if current_bg in [Colors.BG_SECONDARY, "#f9fafb", "#111827"]:
                        widget.configure(bg=theme["bg_secondary"])
                    elif current_bg in [Colors.BG_TERTIARY, "#f3f4f6", "#374151"]:
                        widget.configure(bg=theme["bg_tertiary"])
                    elif current_bg in light_colors["bg"] or current_bg in dark_colors["bg"]:
                        widget.configure(bg=theme["bg_primary"])
                    
                    # Cambiar texto si es un color de tema
                    if current_fg in light_colors["fg"] or current_fg in dark_colors["fg"]:
                        # Determinar si es texto primario o secundario
                        if current_fg in [Colors.TEXT_PRIMARY, "#1f2937", "#f9fafb"]:
                            widget.configure(fg=theme["text_primary"])
                        elif current_fg in [Colors.TEXT_SECONDARY, "#6b7280", "#d1d5db"]:
                            widget.configure(fg=theme["text_secondary"])
                        else:
                            widget.configure(fg=theme["text_primary"])
                except:
                    pass
            elif widget_type == "Button":
                try:
                    current_bg = widget.cget("bg")
                    # Solo cambiar botones secundarios
                    if current_bg in light_colors["bg"] or current_bg in dark_colors["bg"]:
                        widget.configure(bg=theme["btn_secondary_bg"], fg=theme["btn_secondary_fg"])
                except:
                    pass
            
            # Aplicar recursivamente a los hijos
            try:
                for child in widget.winfo_children():
                    self.apply_theme_to_widget(child, theme_name)
            except (tk.TclError, AttributeError):
                pass
        except (tk.TclError, AttributeError):
            # Ignorar errores en widgets destruidos o sin configuración
            pass


# Instancia global del gestor de temas
theme_manager = ThemeManager()

