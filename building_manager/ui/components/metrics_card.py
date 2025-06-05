import tkinter as tk
from tkinter import ttk

class MetricsCard(ttk.Frame):
    """
    Componente para mostrar métricas y estadísticas con estilo Material Design.
    """
    def __init__(self, parent, title, value, subtitle=None, icon=None):
        super().__init__(parent, relief="solid", borderwidth=1)
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de la tarjeta de métricas."""
        # Contenedor principal con padding
        self.configure(padding=(10, 8))
        
        # Frame superior para icono y valor
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X)
        
        # Icono y valor en la misma fila
        if self.icon:
            self.icon_label = ttk.Label(
                top_frame,
                text=self.icon,
                font=("Segoe UI", 16)
            )
            self.icon_label.pack(side=tk.LEFT)
        
        self.value_label = ttk.Label(
            top_frame,
            text=self.value,
            font=("Segoe UI", 24, "bold")
        )
        self.value_label.pack(side=tk.RIGHT)
        
        # Frame inferior para título y subtítulo
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Título
        self.title_label = ttk.Label(
            bottom_frame,
            text=self.title,
            font=("Segoe UI", 12, "bold")
        )
        self.title_label.pack(anchor=tk.W)
        
        # Subtítulo (si se proporciona)
        if self.subtitle:
            self.subtitle_label = ttk.Label(
                bottom_frame,
                text=self.subtitle,
                font=("Segoe UI", 10)
            )
            self.subtitle_label.pack(anchor=tk.W, pady=(1, 0))
        
        # Configurar hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Efecto al pasar el mouse por encima."""
        self.configure(relief="sunken")

    def _on_leave(self, event):
        """Efecto al quitar el mouse."""
        self.configure(relief="solid")

    def update_value(self, new_value):
        """Actualiza el valor mostrado en la métrica."""
        self.value = new_value
        self.value_label.configure(text=str(new_value))

    def update_subtitle(self, new_subtitle):
        """Actualiza el subtítulo de la métrica."""
        self.subtitle = new_subtitle
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.configure(text=new_subtitle) 