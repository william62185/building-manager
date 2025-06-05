import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from typing import Any, Optional

class MetricsCard(ttk.Frame):
    """
    Componente para mostrar métricas y estadísticas con estilo Material Design.
    """
    def __init__(
        self,
        master: Any,
        title: str,
        value: Any,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        color: str = "primary"
    ):
        super().__init__(master)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.color = color
        
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de la tarjeta de métricas."""
        # Contenedor principal ALTURA OPTIMIZADA
        self.configure(
            padding="12 18",  # Padding reducido pero rectangular
            bootstyle=self.color
        )

        # Frame superior para icono y valor - ALTURA REDUCIDA
        top_frame = ttk.Frame(self, bootstyle=self.color)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        # Icono (si se proporciona) - TAMAÑO OPTIMIZADO
        if self.icon:
            icon_label = ttk.Label(
                top_frame,
                text=self.icon,
                font=("Segoe UI Symbol", 20),  # Icono más pequeño
                bootstyle=self.color
            )
            icon_label.pack(side=tk.LEFT, pady=2)

        # Valor principal - TAMAÑO OPTIMIZADO
        self.value_label = ttk.Label(
            top_frame,
            text=str(self.value),
            font=("Segoe UI", 22, "bold"),  # Valor más pequeño
            bootstyle=self.color
        )
        self.value_label.pack(side=tk.RIGHT, pady=2)

        # Frame inferior para título y subtítulo - ALTURA REDUCIDA
        bottom_frame = ttk.Frame(self, bootstyle=self.color)
        bottom_frame.pack(fill=tk.X, pady=(0, 2))

        # Título - TAMAÑO OPTIMIZADO
        title_label = ttk.Label(
            bottom_frame,
            text=self.title,
            font=("Segoe UI", 11, "bold"),  # Título más pequeño
            bootstyle=self.color
        )
        title_label.pack(anchor=tk.W)

        # Subtítulo (si se proporciona) - TAMAÑO OPTIMIZADO
        if self.subtitle:
            self.subtitle_label = ttk.Label(
                bottom_frame,
                text=self.subtitle,
                font=("Segoe UI", 9),  # Subtítulo más pequeño
                bootstyle=self.color
            )
            self.subtitle_label.pack(anchor=tk.W, pady=(1, 0))

    def update_value(self, new_value: Any):
        """Actualiza el valor de la métrica."""
        self.value = new_value
        self.value_label.configure(text=str(new_value))

    def update_subtitle(self, new_subtitle: str):
        """Actualiza el subtítulo de la métrica."""
        self.subtitle = new_subtitle
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.configure(text=new_subtitle) 