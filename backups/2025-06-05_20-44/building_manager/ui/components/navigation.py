import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from typing import Any, Callable, Dict, List

class Navigation(ttk.Frame):
    """
    Componente de navegación con estilo Material Design.
    """
    def __init__(
        self,
        master: Any,
        items: List[Dict[str, Any]],  # [{"id": str, "label": str, "icon": str}, ...]
        on_select: Callable[[str], None],
        active_id: str = None
    ):
        super().__init__(master)
        self.items = items
        self.on_select = on_select
        self.active_id = active_id
        self.buttons: Dict[str, ttk.Button] = {}
        
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de navegación."""
        # Contenedor principal
        self.configure(padding="10")

        # Logo o título de la aplicación
        app_title = ttk.Label(
            self,
            text="Building Manager",
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        app_title.pack(pady=(0, 20), anchor=tk.W)

        # Botones de navegación
        for item in self.items:
            btn = ttk.Button(
                self,
                text=f"{item['icon']} {item['label']}" if 'icon' in item else item['label'],
                command=lambda id=item['id']: self._handle_select(id),
                bootstyle=f"{'primary' if item['id'] == self.active_id else 'secondary'}-link",
                width=25
            )
            btn.pack(pady=2, anchor=tk.W)
            self.buttons[item['id']] = btn

    def set_active(self, item_id: str):
        """Establece el ítem activo."""
        if self.active_id == item_id:
            return

        # Actualizar estilos
        if self.active_id and self.active_id in self.buttons:
            self.buttons[self.active_id].configure(bootstyle="secondary-link")
        
        if item_id in self.buttons:
            self.buttons[item_id].configure(bootstyle="primary-link")
            self.active_id = item_id

    def _handle_select(self, item_id: str):
        """Maneja la selección de un ítem."""
        self.set_active(item_id)
        self.on_select(item_id)

class TopBar(ttk.Frame):
    """
    Barra superior con título y acciones.
    """
    def __init__(
        self,
        master: Any,
        title: str,
        actions: List[Dict[str, Any]] = None  # [{"label": str, "command": Callable, "style": str}, ...]
    ):
        super().__init__(master)
        self.title = title
        self.actions = actions or []
        
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de la barra superior."""
        # Contenedor principal con estilo y sombra
        self.configure(padding="15 10", bootstyle="light")

        # Frame interno con mejor estilo
        content_frame = ttk.Frame(self, bootstyle="light")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Título CENTRADO y más elegante
        title_frame = ttk.Frame(content_frame, bootstyle="light")
        title_frame.pack(expand=True, fill=tk.BOTH)

        # Título mejorado y centrado - TAMAÑO AUMENTADO
        title_text = "📊 Dashboard Manager" if self.title == "Dashboard" else self.title
        
        self.title_label = ttk.Label(
            title_frame,
            text=title_text,
            font=("Segoe UI", 32, "bold"),  # Aumentado de 26 a 32
            bootstyle="primary",
            anchor="center"
        )
        self.title_label.pack(expand=True, pady=12)  # Aumentado el padding

        # Separador vertical
        if self.actions:
            ttk.Separator(content_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=15)

        # Acciones con mejor estilo
        if self.actions:
            actions_frame = ttk.Frame(content_frame, bootstyle="light")
            actions_frame.pack(side=tk.RIGHT, fill=tk.Y)

            for action in self.actions:
                btn = ttk.Button(
                    actions_frame,
                    text=action["label"],
                    command=action["command"],
                    bootstyle=action.get("style", "primary-outline")
                )
                btn.pack(side=tk.RIGHT, padx=5)

    def update_title(self, new_title: str):
        """Actualiza el título de la barra."""
        self.title = new_title
        title_text = "📊 Dashboard Manager" if new_title == "Dashboard" else new_title
        if hasattr(self, 'title_label'):
            self.title_label.configure(text=title_text) 