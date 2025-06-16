"""
Sistema de temas profesional para Building Manager
Paleta de colores moderna y componentes elegantes
"""

import tkinter as tk
from typing import Dict, Any

class Colors:
    """Paleta de colores profesional basada en design systems modernos"""
    
    # COLORES PRIMARIOS
    PRIMARY_50 = "#eff6ff"
    PRIMARY_100 = "#dbeafe" 
    PRIMARY_500 = "#3b82f6"
    PRIMARY_600 = "#2563eb"
    PRIMARY_700 = "#1d4ed8"
    PRIMARY_900 = "#1e3a8a"
    
    # GRISES NEUTROS
    GRAY_50 = "#f9fafb"
    GRAY_100 = "#f3f4f6"
    GRAY_200 = "#e5e7eb"
    GRAY_300 = "#d1d5db"
    GRAY_400 = "#9ca3af"
    GRAY_500 = "#6b7280"
    GRAY_600 = "#4b5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1f2937"
    GRAY_900 = "#111827"
    
    # COLORES SEMÁNTICOS
    SUCCESS_50 = "#ecfdf5"
    SUCCESS_500 = "#10b981"
    SUCCESS_600 = "#059669"
    
    WARNING_50 = "#fffbeb"
    WARNING_500 = "#f59e0b"
    WARNING_600 = "#d97706"
    
    ERROR_50 = "#fef2f2"
    ERROR_500 = "#ef4444"
    ERROR_600 = "#dc2626"
    
    INFO_50 = "#eff6ff"
    INFO_500 = "#3b82f6"
    INFO_600 = "#2563eb"
    
    # BLANCOS Y SOMBRAS
    WHITE = "#ffffff"
    BLACK = "#000000"
    SHADOW_LIGHT = "#00000010"
    SHADOW_MEDIUM = "#00000020"
    SHADOW_DARK = "#00000030"

class Typography:
    """Sistema de tipografía profesional"""
    
    # FAMILIAS DE FUENTES
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
    
    # TAMAÑOS Y PESOS
    SIZES = {
        "xs": 10,
        "sm": 11,
        "base": 12,
        "lg": 14,
        "xl": 16,
        "2xl": 18,
        "3xl": 20,
        "4xl": 24,
        "5xl": 32
    }
    
    WEIGHTS = {
        "normal": "normal",
        "bold": "bold"
    }
    
    @classmethod
    def get_font(cls, size: str = "base", weight: str = "normal") -> tuple:
        """Obtiene configuración de fuente"""
        return (cls.FONT_FAMILY, cls.SIZES[size], cls.WEIGHTS[weight])

class Spacing:
    """Sistema de espaciado consistente"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32

class BorderRadius:
    """Radios de borde para componentes"""
    NONE = 0
    SM = 4
    MD = 6
    LG = 8
    XL = 12
    FULL = 9999

class ThemeManager:
    """Gestor central de temas y estilos"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme()
        }
    
    def _get_light_theme(self) -> Dict[str, Any]:
        """Tema claro profesional"""
        return {
            # BACKGROUNDS
            "bg_primary": Colors.WHITE,
            "bg_secondary": Colors.GRAY_50,
            "bg_tertiary": Colors.GRAY_100,
            "bg_accent": Colors.PRIMARY_50,
            
            # TEXTOS
            "text_primary": Colors.GRAY_900,
            "text_secondary": Colors.GRAY_600,
            "text_tertiary": Colors.GRAY_400,
            "text_accent": Colors.PRIMARY_600,
            
            # BORDES
            "border_light": Colors.GRAY_200,
            "border_medium": Colors.GRAY_300,
            "border_accent": Colors.PRIMARY_100,
            
            # ESTADOS
            "success": Colors.SUCCESS_500,
            "warning": Colors.WARNING_500,
            "error": Colors.ERROR_500,
            "info": Colors.INFO_500,
            
            # BOTONES
            "btn_primary_bg": Colors.PRIMARY_600,
            "btn_primary_fg": Colors.WHITE,
            "btn_primary_hover": Colors.PRIMARY_700,
            
            "btn_secondary_bg": Colors.WHITE,
            "btn_secondary_fg": Colors.GRAY_700,
            "btn_secondary_hover": Colors.GRAY_50,
            "btn_secondary_border": Colors.GRAY_300,
            
            "btn_pdf_bg": Colors.PRIMARY_900,
            "btn_pdf_fg": Colors.WHITE,
            "btn_pdf_hover": Colors.PRIMARY_700,
            
            # INPUTS
            "input_bg": Colors.WHITE,
            "input_border": Colors.GRAY_300,
            "input_border_focus": Colors.PRIMARY_500,
            "input_text": Colors.GRAY_900,
            
            # SOMBRAS
            "shadow_sm": Colors.SHADOW_LIGHT,
            "shadow_md": Colors.SHADOW_MEDIUM,
            "shadow_lg": Colors.SHADOW_DARK,
        }
    
    def _get_dark_theme(self) -> Dict[str, Any]:
        """Tema oscuro profesional (futuro)"""
        return {
            "bg_primary": Colors.GRAY_900,
            "bg_secondary": Colors.GRAY_800,
            "text_primary": Colors.WHITE,
            "text_secondary": Colors.GRAY_300,
            # ... resto de colores para tema oscuro
        }
    
    def get_style(self, component: str) -> Dict[str, Any]:
        """Obtiene estilos para un componente específico"""
        theme = self.themes[self.current_theme]
        
        styles = {
            "window": {
                "bg": theme["bg_primary"]
            },
            
            "frame": {
                "bg": theme["bg_primary"],
                "relief": "flat",
                "bd": 0
            },
            
            "card": {
                "bg": theme["bg_primary"],
                "relief": "solid",
                "bd": 1,
                "highlightbackground": theme["border_light"],
                "highlightthickness": 1,
                "padx": Spacing.SM,
                "pady": Spacing.SM
            },
            
            "label_title": {
                "bg": theme["bg_primary"],
                "fg": theme["text_primary"],
                "font": Typography.get_font("xl", "bold"),
                "anchor": "w"
            },
            
            "label_subtitle": {
                "bg": theme["bg_primary"],
                "fg": theme["text_secondary"],
                "font": Typography.get_font("lg"),
                "anchor": "w"
            },
            
            "label_body": {
                "bg": theme["bg_primary"],
                "fg": theme["text_primary"],
                "font": Typography.get_font("base"),
                "anchor": "w"
            },
            
            "button_primary": {
                "bg": theme["btn_primary_bg"],
                "fg": theme["btn_primary_fg"],
                "font": Typography.get_font("base", "bold"),
                "relief": "flat",
                "bd": 0,
                "padx": Spacing.LG,
                "pady": Spacing.MD,
                "cursor": "hand2",
                "activebackground": theme["btn_primary_hover"],
                "activeforeground": theme["btn_primary_fg"]
            },
            
            "button_secondary": {
                "bg": theme["btn_secondary_bg"],
                "fg": theme["btn_secondary_fg"],
                "font": Typography.get_font("base"),
                "relief": "solid",
                "bd": 1,
                "highlightbackground": theme["btn_secondary_border"],
                "padx": Spacing.LG,
                "pady": Spacing.MD,
                "cursor": "hand2",
                "activebackground": theme["btn_secondary_hover"],
                "activeforeground": theme["btn_secondary_fg"]
            },
            
            "button_pdf": {
                "bg": theme["btn_pdf_bg"],
                "fg": theme["btn_pdf_fg"],
                "activebackground": theme["btn_pdf_hover"],
                "activeforeground": theme["btn_pdf_fg"],
                "relief": "flat",
                "bd": 0,
                "font": Typography.get_font("base", "bold"),
                "padx": Spacing.LG,
                "pady": Spacing.SM,
                "cursor": "hand2"
            },
            
            "entry": {
                "bg": theme["input_bg"],
                "fg": theme["input_text"],
                "font": Typography.get_font("base"),
                "relief": "solid",
                "bd": 1,
                "highlightbackground": theme["input_border"],
                "highlightcolor": theme["input_border_focus"],
                "highlightthickness": 1,
                "insertbackground": theme["text_primary"]
            },
            
            "text": {
                "bg": theme["input_bg"],
                "fg": theme["input_text"],
                "font": Typography.get_font("base"),
                "relief": "solid",
                "bd": 1,
                "highlightbackground": theme["input_border"],
                "highlightcolor": theme["input_border_focus"],
                "highlightthickness": 1,
                "insertbackground": theme["text_primary"],
                "wrap": "word"
            },
            
            "listbox": {
                "bg": theme["bg_primary"],
                "fg": theme["text_primary"],
                "font": Typography.get_font("base"),
                "relief": "solid",
                "bd": 1,
                "highlightbackground": theme["border_light"],
                "selectbackground": theme["bg_accent"],
                "selectforeground": theme["text_accent"]
            },
            
            "treeview": {
                "background": theme["bg_primary"],
                "foreground": theme["text_primary"],
                "fieldbackground": theme["bg_primary"],
                "borderwidth": 1,
                "relief": "solid"
            },
            
            "scrollbar": {
                "bg": theme["bg_secondary"],
                "troughcolor": theme["bg_tertiary"],
                "borderwidth": 0,
                "highlightthickness": 0
            }
        }
        
        return styles.get(component, {})
    
    def apply_hover_effect(self, widget, hover_bg: str = None):
        """Aplica efecto hover a un widget respetando el color del estilo del botón"""
        original_bg = widget.cget("bg")
        # Usar el color de activebackground si está definido
        hover_color = widget.cget("activebackground") if widget.cget("activebackground") else (hover_bg or original_bg)
        def on_enter(e):
            widget.config(bg=hover_color)
        def on_leave(e):
            widget.config(bg=original_bg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_gradient_frame(self, parent, color1: str, color2: str) -> tk.Frame:
        """Crea un frame con efecto degradado (simulado)"""
        frame = tk.Frame(parent, bg=color1, height=2)
        return frame

# Instancia global del gestor de temas
theme_manager = ThemeManager() 