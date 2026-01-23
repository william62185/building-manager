"""
Widgets modernos para Building Manager Pro
Componentes reutilizables con diseño profesional
"""

import tkinter as tk
from typing import Dict, Any, List, Optional, Callable
from .theme_manager import theme_manager, Spacing, Colors
from .icons import Icons


class ModernButton(tk.Frame):
    """Botón moderno con icono y estilo personalizable"""
    
    def __init__(self, parent, text: str = "", icon: str = "", style: str = "primary", 
                 command: Callable = None, small: bool = False):
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Determinar colores según estilo
        if style == "primary":
            bg = theme["btn_primary_bg"]
            fg = theme["btn_primary_fg"]
            hover_bg = theme.get("btn_primary_hover", Colors.PRIMARY_DARK)
        elif style == "secondary":
            bg = theme["btn_secondary_bg"]
            fg = theme["btn_secondary_fg"]
            hover_bg = theme.get("btn_secondary_hover", Colors.BG_TERTIARY)
        elif style == "warning":
            bg = Colors.WARNING
            fg = "#ffffff"
            hover_bg = "#d97706"
        elif style == "danger":
            bg = Colors.ERROR
            fg = "#ffffff"
            hover_bg = "#dc2626"
        elif style == "pdf":
            bg = "#dc2626"
            fg = "#ffffff"
            hover_bg = "#b91c1c"
        else:
            bg = theme["btn_primary_bg"]
            fg = theme["btn_primary_fg"]
            hover_bg = theme.get("btn_primary_hover", Colors.PRIMARY_DARK)
        
        super().__init__(parent, bg=bg, relief="flat", bd=0)
        
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        
        # Contenedor interno
        inner = tk.Frame(self, bg=bg)
        inner.pack(fill="both", expand=True, padx=Spacing.MD if not small else Spacing.SM, 
                   pady=Spacing.SM if not small else Spacing.XS)
        
        # Icono
        if icon:
            icon_label = tk.Label(inner, text=icon, bg=bg, fg=fg, 
                                 font=("Segoe UI Symbol", 12 if not small else 10))
            icon_label.pack(side="left", padx=(0, Spacing.XS if text else 0))
        
        # Texto
        if text:
            text_label = tk.Label(inner, text=text, bg=bg, fg=fg,
                                 font=("Segoe UI", 10 if small else 11, "bold"))
            text_label.pack(side="left")
        
        # Bind events - función auxiliar para vincular a todos los widgets recursivamente
        def bind_to_all_widgets(widget, event, handler):
            """Vincular evento a un widget y todos sus hijos recursivamente"""
            widget.bind(event, handler)
            widget.configure(cursor="hand2")
            for child in widget.winfo_children():
                bind_to_all_widgets(child, event, handler)
        
        def on_enter(e):
            self.configure(bg=self.hover_bg)
            inner.configure(bg=self.hover_bg)
            for widget in inner.winfo_children():
                widget.configure(bg=self.hover_bg)
        
        def on_leave(e):
            self.configure(bg=self.bg)
            inner.configure(bg=self.bg)
            for widget in inner.winfo_children():
                widget.configure(bg=self.bg)
        
        def on_click(e):
            if self.command:
                self.command()
            return "break"  # Prevenir propagación del evento
        
        # Vincular eventos a todo el botón y sus hijos
        bind_to_all_widgets(self, "<Enter>", on_enter)
        bind_to_all_widgets(self, "<Leave>", on_leave)
        bind_to_all_widgets(self, "<Button-1>", on_click)


class ModernCard(tk.Frame):
    """Tarjeta moderna con sombra y estilo profesional"""
    
    def __init__(self, parent, title=None, **kwargs):
        theme = theme_manager.themes[theme_manager.current_theme]
        super().__init__(parent, bg=theme["bg_primary"], relief="flat", bd=1,
                        highlightbackground=theme["border_light"], **kwargs)
        
        # Contenedor interno para el contenido
        self.content_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        self.content_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        # Título opcional
        if title:
            title_label = tk.Label(
                self.content_frame,
                text=title,
                **theme_manager.get_style("label_title")
            )
            title_label.pack(anchor="w", pady=(0, Spacing.MD))


class ModernEntry(tk.Entry):
    """Campo de entrada moderno"""
    
    def __init__(self, parent, placeholder: str = "", **kwargs):
        theme = theme_manager.themes[theme_manager.current_theme]
        default_kwargs = {
            "bg": theme["bg_primary"],
            "fg": theme["text_primary"],
            "font": ("Segoe UI", 11),
            "relief": "solid",
            "bd": 1,
            "highlightthickness": 0,
            "insertbackground": theme["text_primary"]
        }
        default_kwargs.update(kwargs)
        super().__init__(parent, **default_kwargs)
        
        if placeholder:
            self.insert(0, placeholder)
            self.configure(fg=theme["text_secondary"])
            self.bind("<FocusIn>", lambda e: self._on_focus_in(placeholder))
            self.bind("<FocusOut>", lambda e: self._on_focus_out(placeholder))
    
    def _on_focus_in(self, placeholder):
        theme = theme_manager.themes[theme_manager.current_theme]
        if self.get() == placeholder:
            self.delete(0, tk.END)
            self.configure(fg=theme["text_primary"])
    
    def _on_focus_out(self, placeholder):
        theme = theme_manager.themes[theme_manager.current_theme]
        if not self.get():
            self.insert(0, placeholder)
            self.configure(fg=theme["text_secondary"])


class ModernBadge(tk.Label):
    """Badge moderno para mostrar estados"""
    
    def __init__(self, parent, text: str, style: str = "neutral"):
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Colores según estilo
        if style == "success":
            bg = Colors.SUCCESS
            fg = "#ffffff"
        elif style == "danger":
            bg = Colors.ERROR
            fg = "#ffffff"
        elif style == "warning":
            bg = Colors.WARNING
            fg = "#ffffff"
        elif style == "info":
            bg = Colors.INFO
            fg = "#ffffff"
        else:  # neutral
            bg = theme["bg_tertiary"]
            fg = theme["text_primary"]
        
        super().__init__(parent, text=text, bg=bg, fg=fg,
                        font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                        padx=Spacing.SM, pady=Spacing.XS)


class ModernSeparator(tk.Frame):
    """Separador moderno"""
    
    def __init__(self, parent, orientation: str = "vertical"):
        theme = theme_manager.themes[theme_manager.current_theme]
        if orientation == "vertical":
            super().__init__(parent, width=1, bg=theme["border_light"], relief="flat")
            self.pack(side="left", fill="y", padx=Spacing.MD)
        else:
            super().__init__(parent, height=1, bg=theme["border_light"], relief="flat")
            self.pack(fill="x", pady=Spacing.MD)


class ModernMetricCard(tk.Frame):
    """Tarjeta de métrica moderna"""
    
    def __init__(self, parent, title: str, value: str, icon: str = "", 
                 color_theme: str = "primary"):
        theme = theme_manager.themes[theme_manager.current_theme]
        # Card con borde más visible y fondo blanco profesional
        super().__init__(parent, bg="white", relief="flat", bd=1,
                        highlightbackground=theme["border_light"],
                        highlightthickness=1)
        
        # Contenedor interno con padding reducido (1/3 menos)
        inner = tk.Frame(self, bg="white")
        inner.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Header con icono y título en la misma línea
        header = tk.Frame(inner, bg="white")
        header.pack(fill="x", pady=(0, Spacing.XS))
        
        if icon:
            icon_label = tk.Label(header, text=icon, bg="white",
                                 font=("Segoe UI Symbol", 12))
            icon_label.pack(side="left", padx=(0, Spacing.XS))
        
        title_label = tk.Label(header, text=title, bg="white",
                              fg=theme["text_secondary"], font=("Segoe UI", 8))
        title_label.pack(side="left", fill="x", expand=True)
        
        # Valor destacado (reducido 1/3)
        value_label = tk.Label(inner, text=value, bg="white",
                             fg=theme["text_primary"], font=("Segoe UI", 14, "bold"))
        value_label.pack(anchor="w")


class DetailedMetricCard(tk.Frame):
    """Tarjeta de métrica con detalles"""
    
    def __init__(self, parent, title: str, total_value: str, details: List[Dict[str, Any]],
                 icon: str = "", color_theme: str = "primary"):
        theme = theme_manager.themes[theme_manager.current_theme]
        # Card con borde más visible y fondo blanco profesional
        super().__init__(parent, bg="white", relief="flat", bd=1,
                        highlightbackground=theme["border_light"],
                        highlightthickness=1)
        
        # Contenedor interno con padding reducido (1/3 menos)
        inner = tk.Frame(self, bg="white")
        inner.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Header con icono y título
        header = tk.Frame(inner, bg="white")
        header.pack(fill="x", pady=(0, Spacing.XS))
        
        if icon:
            icon_label = tk.Label(header, text=icon, bg="white",
                                 font=("Segoe UI Symbol", 12))
            icon_label.pack(side="left", padx=(0, Spacing.XS))
        
        title_label = tk.Label(header, text=title, bg="white",
                              fg=theme["text_secondary"], font=("Segoe UI", 8))
        title_label.pack(side="left", fill="x", expand=True)
        
        # Valor total destacado (reducido 1/3)
        total_label = tk.Label(inner, text=total_value, bg="white",
                             fg=theme["text_primary"], font=("Segoe UI", 14, "bold"))
        total_label.pack(anchor="w", pady=(0, Spacing.XS))
        
        # Detalles con espaciado reducido
        details_frame = tk.Frame(inner, bg="white")
        details_frame.pack(fill="x")
        
        for i, detail in enumerate(details):
            detail_row = tk.Frame(details_frame, bg="white")
            detail_row.pack(fill="x", pady=(Spacing.XS if i > 0 else 0, 0))
            
            label = tk.Label(detail_row, text=detail.get("label", ""), 
                           bg="white", fg=theme["text_secondary"],
                           font=("Segoe UI", 7))
            label.pack(side="left")
            
            value = tk.Label(detail_row, text=str(detail.get("value", "")),
                           bg="white", fg=detail.get("color", theme["text_primary"]),
                           font=("Segoe UI", 7, "bold"))
            value.pack(side="right")

