import tkinter as tk
from tkinter import ttk
from ...theme.colors import MaterialColors

class StatCard(ttk.Frame):
    def __init__(
        self,
        parent,
        title: str,
        value: str,
        icon: str,
        color: str = MaterialColors.PRIMARY,
        **kwargs
    ):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        
        # Configurar estilo de la tarjeta
        self.configure(padding="16")
        
        # Contenido de la tarjeta
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)
        
        # Icono
        self.icon_label = ttk.Label(
            content,
            text=icon,
            font=("Segoe UI", 24),
            foreground=color
        )
        self.icon_label.pack(anchor="w")
        
        # Valor
        self.value_label = ttk.Label(
            content,
            text=value,
            font=("Segoe UI", 32, "bold"),
            foreground=MaterialColors.TEXT_PRIMARY
        )
        self.value_label.pack(anchor="w", pady=(5, 0))
        
        # Título
        self.title_label = ttk.Label(
            content,
            text=title,
            font=("Segoe UI", 12),
            foreground=MaterialColors.TEXT_SECONDARY
        )
        self.title_label.pack(anchor="w", pady=(5, 0))
        
        # Configurar eventos de hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, event):
        """Efecto al pasar el mouse por encima"""
        self.configure(style="CardHover.TFrame")
        
    def _on_leave(self, event):
        """Efecto al quitar el mouse"""
        self.configure(style="Card.TFrame")
        
    def update_value(self, new_value: str):
        """Actualiza el valor mostrado en la tarjeta"""
        self.value_label.configure(text=new_value)
        
    @classmethod
    def setup_styles(cls):
        """Configura los estilos necesarios para las tarjetas"""
        style = ttk.Style()
        
        # Estilo normal
        style.configure(
            "Card.TFrame",
            background=MaterialColors.CARD,
            relief="raised",
            borderwidth=1
        )
        
        # Estilo hover
        style.configure(
            "CardHover.TFrame",
            background=MaterialColors.get_hover_color(MaterialColors.CARD),
            relief="solid",
            borderwidth=1
        ) 