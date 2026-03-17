"""
Vista de PRUEBA — Layout base con tabs ancladas.
================================================
Sirve como plantilla para nuevos módulos.

Estructura visual:
  ┌─────────────────────────────────────────────────────┐
  │ [Tab 1] [Tab 2] [Tab 3]          [🏠 Inicio]        │  ← tab_bar (con borde inferior)
  ├─────────────────────────────────────────────────────┤
  │                                                     │
  │              Contenido del tab activo               │  ← content_panel
  │                                                     │
  └─────────────────────────────────────────────────────┘

Convenciones:
- Lazy load: cada sub-vista se instancia solo al primer clic
- Botón "🏠 Inicio" reemplaza al antiguo "🏠 Dashboard" (más compacto)
- Tabs con borde inferior para anclarlas visualmente al contenido
"""
import tkinter as tk

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.logger import logger

# ---------------------------------------------------------------------------
# Definición de tabs: (clave, icono, etiqueta)
# ---------------------------------------------------------------------------
_TABS = [
    ("tab1", "📋", "Sección uno"),
    ("tab2", "📊", "Sección dos"),
    ("tab3", "⚙️",  "Sección tres"),
    ("tab4", "📁", "Sección cuatro"),
]

# Módulo para colores (cambiar al nombre real del módulo)
_MODULE = "administración"

# Colores de la barra de tabs
_TAB_BAR_BG   = "#e8ecf0"   # fondo de la barra (ligeramente más oscuro que content_bg)
_TAB_BAR_BORDER = "#c5cdd6"  # borde inferior de la barra


class PruebaView(tk.Frame):
    """Vista de prueba con layout de tabs ancladas."""

    def __init__(self, parent, on_navigate=None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)
        self.on_navigate = on_navigate

        self._active_tab = None
        self._tab_buttons = {}
        self._loaded_views = {}

        self._build_layout()
        self._select_tab(_TABS[0][0])   # seleccionar primera tab por defecto

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        colors = get_module_colors(_MODULE)

        # ── Barra de tabs ──────────────────────────────────────────────
        # Fondo diferenciado + borde inferior que "ancla" las tabs
        tab_bar_outer = tk.Frame(self, bg=_TAB_BAR_BORDER)
        tab_bar_outer.pack(fill="x")

        # Frame interior con el fondo de la barra (el borde inferior es el
        # 1px del frame exterior que queda visible abajo)
        self._tab_bar = tk.Frame(tab_bar_outer, bg=_TAB_BAR_BG)
        self._tab_bar.pack(fill="x", side="top", pady=(0, 1))

        # Tabs a la izquierda
        tabs_left = tk.Frame(self._tab_bar, bg=_TAB_BAR_BG)
        tabs_left.pack(side="left", fill="y")

        for key, icon, label in _TABS:
            self._create_tab_button(tabs_left, key, icon, label)

        # Botón "🏠 Inicio" compacto a la derecha
        btn_inicio = create_rounded_button(
            self._tab_bar,
            text="🏠 Inicio",
            bg_color=colors["primary"],
            fg_color="white",
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._go_to_inicio,
            padx=10,
            pady=4,
            radius=4,
            border_color="#000000",
        )
        btn_inicio.pack(side="right", padx=Spacing.SM, pady=Spacing.XS)

        # ── Panel de contenido ─────────────────────────────────────────
        self._content_panel = tk.Frame(self, bg=self._bg)
        self._content_panel.pack(fill="both", expand=True,
                                  padx=Spacing.MD, pady=Spacing.SM)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _create_tab_button(self, parent, key, icon, label):
        colors = get_module_colors(_MODULE)
        theme = theme_manager.themes[theme_manager.current_theme]

        btn = tk.Button(
            parent,
            text=f"{icon}  {label}",
            font=("Segoe UI", 12),
            bg=_TAB_BAR_BG,
            fg=theme["text_primary"],
            activebackground=colors["light"],
            activeforeground=theme["text_primary"],
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda k=key: self._select_tab(k),
        )
        btn.pack(side="left")

        btn.bind("<Enter>", lambda e, b=btn, k=key: self._on_tab_enter(b, k))
        btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_tab_leave(b, k))
        self._tab_buttons[key] = btn

    def _on_tab_enter(self, btn, key):
        if key == self._active_tab:
            return
        colors = get_module_colors(_MODULE)
        btn.config(bg=colors["light"])

    def _on_tab_leave(self, btn, key):
        if key == self._active_tab:
            return
        btn.config(bg=_TAB_BAR_BG)

    def _select_tab(self, key):
        colors = get_module_colors(_MODULE)
        theme = theme_manager.themes[theme_manager.current_theme]

        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.config(
                    bg=colors["primary"],
                    fg="white",
                    font=("Segoe UI", 12, "bold"),
                    activebackground=colors["primary"],
                    activeforeground="white",
                )
            else:
                btn.config(
                    bg=_TAB_BAR_BG,
                    fg=theme["text_primary"],
                    font=("Segoe UI", 12),
                    activebackground=colors["light"],
                    activeforeground=theme["text_primary"],
                )

        self._active_tab = key

        # Ocultar contenido anterior
        for child in self._content_panel.winfo_children():
            child.pack_forget()

        # Lazy load
        if key not in self._loaded_views:
            try:
                view = self._build_tab_content(key)
                if view:
                    self._loaded_views[key] = view
            except Exception as exc:
                logger.exception("Error al cargar tab '%s': %s", key, exc)
                return

        view = self._loaded_views.get(key)
        if view:
            view.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Contenido de cada tab (placeholder — reemplazar con sub-vistas reales)
    # ------------------------------------------------------------------

    def _build_tab_content(self, key):
        """Instancia el contenido del tab. Reemplazar con sub-vistas reales."""
        theme = theme_manager.themes[theme_manager.current_theme]
        frame = tk.Frame(self._content_panel, bg=self._bg)

        label_text = {
            "tab1": "Contenido de Sección uno",
            "tab2": "Contenido de Sección dos",
            "tab3": "Contenido de Sección tres",
            "tab4": "Contenido de Sección cuatro",
        }.get(key, key)

        tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 14),
            bg=self._bg,
            fg=theme["text_secondary"],
        ).pack(expand=True)

        return frame

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def _go_to_inicio(self):
        if self.on_navigate:
            self.on_navigate("dashboard")
