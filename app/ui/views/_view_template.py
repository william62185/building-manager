"""
TEMPLATE DE VISTA — Building Manager Pro
=========================================
Copia este archivo, renómbralo y reemplaza los TODOs.

Convenciones obligatorias:
- Fondo: theme.get("content_bg") — nunca hardcodear colores de fondo
- Logging: usar `logger`, nunca `print`
- Combobox: siempre llamar bind_combobox_dropdown_on_click() tras crear uno
- Rutas: siempre vía paths_config (DATA_DIR, etc.)
- Callbacks estándar: on_back, on_navigate, on_data_change
"""

import tkinter as tk
from tkinter import ttk, messagebox

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
# from manager.app.ui.components.modern_widgets import bind_combobox_dropdown_on_click  # si usas comboboxes
from manager.app.logger import logger

# TODO: cambiar "modulo" por el nombre real: "pagos", "gastos", "inquilinos",
#       "contabilidad", "administración"
_MODULE = "administración"


class MyNewView(tk.Frame):  # TODO: renombrar la clase
    """TODO: descripción breve de la vista."""

    def __init__(self, parent, on_back=None, on_navigate=None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)

        self.on_back = on_back
        self.on_navigate = on_navigate

        self._build_layout()

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        bg = self._bg
        colors = get_module_colors(_MODULE)

        # --- Barra superior: Dashboard a la derecha ---
        top_bar = tk.Frame(self, bg=bg)
        top_bar.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, Spacing.SM))

        create_rounded_button(
            top_bar,
            text="🏠 Dashboard",
            bg_color=colors["primary"],
            fg_color="white",
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._go_to_dashboard,
            padx=14, pady=6, radius=4,
            border_color="#000000",
        ).pack(side="right")

        # Opcional: botón Volver
        # create_rounded_button(top_bar, text="← Volver", ..., command=self._on_back).pack(side="right", padx=(0, 8))

        # --- Separador ---
        tk.Frame(self, height=1, bg=theme_manager.themes[theme_manager.current_theme].get("border_light", "#e0e0e0")).pack(fill="x", padx=Spacing.MD)

        # --- Área de contenido ---
        self._content = tk.Frame(self, bg=bg)
        self._content.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.SM)

        self._build_content(self._content)

    def _build_content(self, parent):
        """TODO: construir el contenido principal aquí."""
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]

        # Ejemplo: label de placeholder
        tk.Label(
            parent,
            text="Contenido de la vista",
            font=("Segoe UI", 13),
            bg=bg,
            fg=theme["text_primary"],
        ).pack(expand=True)

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def _on_back(self):
        if self.on_back:
            self.on_back()

    def _go_to_dashboard(self):
        if self.on_navigate:
            self.on_navigate("dashboard")
