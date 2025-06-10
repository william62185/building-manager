"""
Componentes modernos y profesionales para Building Manager
Widgets elegantes con diseño contemporáneo
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any
from .theme_manager import theme_manager, Spacing
from .icons import Icons, IconThemes

class ModernButton(tk.Frame):
    """Botón moderno con iconos y estados elegantes"""
    
    def __init__(self, parent, text: str = "", icon: str = "", 
                 style: str = "primary", command: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.style = style
        self.is_disabled = False
        
        # Configurar el frame principal
        self.configure(**theme_manager.get_style("frame"))
        
        # Crear el botón interno
        self._create_button(text, icon)
        
    def _create_button(self, text: str, icon: str):
        """Crea el botón con estilo moderno"""
        button_style = theme_manager.get_style(f"button_{self.style}")
        
        # Texto del botón con icono
        button_text = f"{icon} {text}" if icon else text
        
        self.button = tk.Button(
            self,
            text=button_text,
            command=self._on_click,
            **button_style
        )
        self.button.pack(fill="both", expand=True)
        
        # Efectos de hover
        theme_manager.apply_hover_effect(self.button)
        
    def _on_click(self):
        """Maneja el click del botón"""
        if not self.is_disabled and self.command:
            self.command()
    
    def set_disabled(self, disabled: bool):
        """Habilita/deshabilita el botón"""
        self.is_disabled = disabled
        state = "disabled" if disabled else "normal"
        self.button.configure(state=state)

class ModernCard(tk.Frame):
    """Tarjeta moderna con sombra y bordes elegantes"""
    
    def __init__(self, parent, title: str = "", subtitle: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Aplicar estilo de card
        self.configure(**theme_manager.get_style("card"))
        
        if title or subtitle:
            self._create_header(title, subtitle)
            
        # Frame para contenido
        self.content_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        self.content_frame.pack(fill="both", expand=True, pady=(Spacing.XS, 0))
        
    def _create_header(self, title: str, subtitle: str):
        """Crea el header de la card"""
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        if title:
            title_label = tk.Label(
                header_frame,
                text=title,
                **theme_manager.get_style("label_title")
            )
            title_label.pack(anchor="w")
            
        if subtitle:
            subtitle_label = tk.Label(
                header_frame,
                text=subtitle,
                **theme_manager.get_style("label_subtitle")
            )
            subtitle_label.pack(anchor="w")

class ModernEntry(tk.Frame):
    """Campo de entrada moderno con etiqueta y validación"""
    
    def __init__(self, parent, label: str = "", placeholder: str = "", 
                 icon: str = "", entry_type: str = "text", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(**theme_manager.get_style("frame"))
        self.entry_type = entry_type
        
        # Crear componentes
        self._create_label(label, icon)
        self._create_entry(placeholder)
        
    def _create_label(self, label: str, icon: str):
        """Crea la etiqueta del campo"""
        if label:
            label_frame = tk.Frame(self, **theme_manager.get_style("frame"))
            label_frame.pack(fill="x", pady=(0, Spacing.XS))
            
            label_text = f"{icon} {label}" if icon else label
            self.label = tk.Label(
                label_frame,
                text=label_text,
                **theme_manager.get_style("label_body")
            )
            self.label.pack(anchor="w")
    
    def _create_entry(self, placeholder: str):
        """Crea el campo de entrada"""
        entry_style = theme_manager.get_style("entry")
        
        if self.entry_type == "text":
            self.entry = tk.Entry(self, **entry_style)
        elif self.entry_type == "password":
            self.entry = tk.Entry(self, show="*", **entry_style)
        elif self.entry_type == "multiline":
            self.entry = tk.Text(self, height=4, **theme_manager.get_style("text"))
        
        self.entry.pack(fill="x", pady=(0, Spacing.SM))
        
        # Placeholder effect
        if placeholder and self.entry_type != "multiline":
            self._add_placeholder(placeholder)
    
    def _add_placeholder(self, placeholder: str):
        """Añade efecto de placeholder"""
        theme = theme_manager.themes[theme_manager.current_theme]
        
        def on_focus_in(event):
            if self.entry.get() == placeholder:
                self.entry.delete(0, tk.END)
                self.entry.configure(fg=theme["text_primary"])
        
        def on_focus_out(event):
            if not self.entry.get():
                self.entry.insert(0, placeholder)
                self.entry.configure(fg=theme["text_tertiary"])
        
        # Configurar placeholder inicial
        self.entry.insert(0, placeholder)
        self.entry.configure(fg=theme["text_tertiary"])
        
        self.entry.bind("<FocusIn>", on_focus_in)
        self.entry.bind("<FocusOut>", on_focus_out)
    
    def get(self) -> str:
        """Obtiene el valor del campo"""
        if self.entry_type == "multiline":
            return self.entry.get("1.0", tk.END).strip()
        return self.entry.get()
    
    def set(self, value: str):
        """Establece el valor del campo"""
        if self.entry_type == "multiline":
            self.entry.delete("1.0", tk.END)
            self.entry.insert("1.0", value)
        else:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, value)

class ModernMetricCard(ModernCard):
    """Tarjeta de métrica con valor destacado"""
    
    def __init__(self, parent, title: str, value: str, icon: str = "", 
                 trend: str = None, color_theme: str = "primary", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.color_theme = color_theme
        self._create_metric_content(title, value, icon, trend)
    
    def _create_metric_content(self, title: str, value: str, icon: str, trend: str):
        """Crea el contenido de la métrica"""
        # Header con icono
        header_frame = tk.Frame(self.content_frame, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        # Icono y título
        title_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        title_frame.pack(side="left")
        
        if icon:
            icon_config = Icons.get_colored_icon(
                icon, 
                IconThemes.PRIMARY["color"] if self.color_theme == "primary" else 
                IconThemes.SUCCESS["color"] if self.color_theme == "success" else
                IconThemes.WARNING["color"] if self.color_theme == "warning" else
                IconThemes.ERROR["color"]
            )
            
            icon_label = tk.Label(
                title_frame,
                text=icon_config["text"],
                font=icon_config["font"],
                fg=icon_config["color"],
                bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            )
            icon_label.pack(side="left", padx=(0, Spacing.SM))
        
        title_label = tk.Label(
            title_frame,
            text=title,
            **theme_manager.get_style("label_body")
        )
        title_label.pack(side="left")
        
        # Valor principal
        value_label = tk.Label(
            self.content_frame,
            text=value,
            **theme_manager.get_style("label_title")
        )
        value_label.configure(font=("Segoe UI", 24, "bold"))
        value_label.pack(anchor="w")
        
        # Tendencia (opcional)
        if trend:
            trend_icon = Icons.TRENDING_UP if "+" in trend else Icons.TRENDING_DOWN
            trend_color = IconThemes.SUCCESS["color"] if "+" in trend else IconThemes.ERROR["color"]
            
            trend_label = tk.Label(
                self.content_frame,
                text=f"{trend_icon} {trend}",
                fg=trend_color,
                bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
                font=("Segoe UI", 12, "normal"),
                anchor="w"
            )
            trend_label.pack(anchor="w", pady=(Spacing.XS, 0))

class ModernProgressBar(tk.Frame):
    """Barra de progreso moderna"""
    
    def __init__(self, parent, value: float = 0, max_value: float = 100, 
                 height: int = 8, color: str = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.value = value
        self.max_value = max_value
        self.height = height
        self.color = color or theme_manager.themes[theme_manager.current_theme]["text_accent"]
        
        self.configure(**theme_manager.get_style("frame"))
        self._create_progress_bar()
    
    def _create_progress_bar(self):
        """Crea la barra de progreso"""
        # Frame de fondo
        bg_frame = tk.Frame(
            self,
            height=self.height,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_tertiary"],
            relief="flat"
        )
        bg_frame.pack(fill="x")
        bg_frame.pack_propagate(False)
        
        # Frame de progreso
        progress_width = int((self.value / self.max_value) * 200)  # 200px de ancho base
        self.progress_frame = tk.Frame(
            bg_frame,
            width=progress_width,
            height=self.height,
            bg=self.color,
            relief="flat"
        )
        self.progress_frame.pack(side="left")
        self.progress_frame.pack_propagate(False)
    
    def set_value(self, value: float):
        """Actualiza el valor de la barra"""
        self.value = min(value, self.max_value)
        progress_width = int((self.value / self.max_value) * 200)
        self.progress_frame.configure(width=progress_width)

class ModernBadge(tk.Label):
    """Badge o etiqueta moderna para estados"""
    
    def __init__(self, parent, text: str, style: str = "primary", **kwargs):
        
        # Obtener colores del tema
        theme_colors = {
            "primary": IconThemes.PRIMARY,
            "success": IconThemes.SUCCESS,
            "warning": IconThemes.WARNING,
            "error": IconThemes.ERROR,
            "neutral": IconThemes.NEUTRAL
        }
        
        colors = theme_colors.get(style, IconThemes.PRIMARY)
        
        # Filtrar kwargs para evitar conflictos
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['bg', 'fg', 'font', 'text']}
        
        super().__init__(
            parent,
            text=text,
            bg=colors["bg"],
            fg=colors["color"],
            font=("Segoe UI", 10, "bold"),
            padx=Spacing.SM,
            pady=Spacing.XS,
            relief="flat",
            **filtered_kwargs
        )

class ModernSeparator(tk.Frame):
    """Separador elegante"""
    
    def __init__(self, parent, orientation: str = "horizontal", **kwargs):
        super().__init__(parent, **kwargs)
        
        theme = theme_manager.themes[theme_manager.current_theme]
        
        if orientation == "horizontal":
            self.configure(height=1, bg=theme["border_light"])
            self.pack(fill="x", pady=Spacing.MD)
        else:
            self.configure(width=1, bg=theme["border_light"])
            self.pack(fill="y", padx=Spacing.MD)

class DetailedMetricCard(ModernCard):
    """Tarjeta de métrica con valor principal y detalles adicionales"""
    
    def __init__(self, parent, title: str, total_value: str, details: list, 
                 icon: str = "", color_theme: str = "primary", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.color_theme = color_theme
        self._create_detailed_metric_content(title, total_value, details, icon)
    
    def _create_detailed_metric_content(self, title: str, total_value: str, details: list, icon: str):
        """Crea el contenido de la métrica detallada"""
        # Header con icono y título
        header_frame = tk.Frame(self.content_frame, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.SM))
        
        if icon:
            icon_config = Icons.get_colored_icon(
                icon, 
                IconThemes.PRIMARY["color"] if self.color_theme == "primary" else 
                IconThemes.SUCCESS["color"] if self.color_theme == "success" else
                IconThemes.WARNING["color"] if self.color_theme == "warning" else
                IconThemes.ERROR["color"]
            )
            
            icon_label = tk.Label(
                header_frame,
                text=icon_config["text"],
                font=icon_config["font"],
                fg=icon_config["color"],
                bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            )
            icon_label.pack(side="left", padx=(0, Spacing.SM))
        
        title_label = tk.Label(
            header_frame,
            text=title,
            **theme_manager.get_style("label_body")
        )
        title_label.pack(side="left")
        
        # Valor principal
        value_label = tk.Label(
            self.content_frame,
            text=total_value,
            **theme_manager.get_style("label_title")
        )
        value_label.configure(font=("Segoe UI", 22, "bold"))
        value_label.pack(anchor="w", pady=(0, Spacing.SM))
        
        # Detalles
        details_frame = tk.Frame(self.content_frame, **theme_manager.get_style("frame"))
        details_frame.pack(fill="x")
        
        for detail in details:
            detail_row = tk.Frame(details_frame, **theme_manager.get_style("frame"))
            detail_row.pack(fill="x", pady=1)
            
            # Indicador de color
            indicator = tk.Frame(
                detail_row,
                bg=detail.get("color", theme_manager.themes[theme_manager.current_theme]["text_secondary"]),
                width=8,
                height=8
            )
            indicator.pack(side="left", padx=(0, Spacing.SM), pady=6)
            
            # Texto del detalle
            detail_label = tk.Label(
                detail_row,
                text=f"{detail['label']}: {detail['value']}",
                font=("Segoe UI", 10),
                fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"],
                bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            )
            detail_label.pack(side="left") 