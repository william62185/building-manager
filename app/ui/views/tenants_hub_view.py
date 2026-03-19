"""
Hub principal del módulo de Inquilinos.
Layout: barra de tabs anclada + panel de contenido (lazy load).

Tabs:
  - Inquilinos      → TenantsView  (lista + búsqueda)
  - Nuevo inquilino → TenantFormView
  - Reportes        → TenantManagementReportsView
"""
import tkinter as tk
from typing import Callable, Optional

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.logger import logger

_TABS = [
    ("lista",     "👥", "Inquilinos"),
    ("nuevo",     "➕", "Nuevo inquilino"),
    ("inactivos", "🚫", "Inactivos"),
    ("reportes",  "📊", "Reportes"),
]

_MODULE         = "inquilinos"
_TAB_BAR_BG     = "#e8ecf0"
_TAB_BAR_BORDER = "#c5cdd6"


class TenantsHubView(tk.Frame):
    """Hub principal del módulo de Inquilinos con tabs de navegación."""

    def __init__(
        self,
        parent,
        on_back: Callable = None,
        on_data_change: Callable = None,
        on_register_payment: Callable = None,
    ):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)

        self.on_back = on_back
        self.on_data_change = on_data_change
        self.on_register_payment = on_register_payment

        self._active_tab: Optional[str] = None
        self._tab_buttons: dict = {}
        self._loaded_views: dict = {}

        self._build_layout()
        self.after(0, lambda: self._select_tab("lista"))

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        colors = get_module_colors(_MODULE)
        theme = theme_manager.themes[theme_manager.current_theme]

        # ── Barra de tabs con borde inferior ──────────────────────────
        tab_bar_outer = tk.Frame(self, bg=_TAB_BAR_BORDER)
        tab_bar_outer.pack(fill="x")

        self._tab_bar = tk.Frame(tab_bar_outer, bg=_TAB_BAR_BG)
        self._tab_bar.pack(fill="x", side="top", pady=(0, 1))

        tabs_left = tk.Frame(self._tab_bar, bg=_TAB_BAR_BG)
        tabs_left.pack(side="left", fill="y")

        for key, icon, label in _TABS:
            self._create_tab_button(tabs_left, key, icon, label)

        # Botones Volver + Inicio a la derecha
        btns_right = tk.Frame(self._tab_bar, bg=_TAB_BAR_BG)
        btns_right.pack(side="right", padx=Spacing.SM, pady=Spacing.XS)

        btn_inicio = create_rounded_button(
            btns_right,
            text="🏠 Inicio",
            bg_color=colors["primary"],
            fg_color="white",
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._go_to_dashboard,
            padx=14,
            pady=7,
            radius=4,
            border_color="#000000",
        )
        btn_inicio.pack(side="right", padx=(4, 0))

        btn_volver = create_rounded_button(
            btns_right,
            text="← Volver",
            bg_color=theme.get("btn_secondary_bg", "#e5e7eb"),
            fg_color=colors["primary"],
            hover_bg=colors["light"],
            hover_fg=colors["primary"],
            command=self._on_volver,
            padx=14,
            pady=7,
            radius=4,
            border_color=colors["light"],
        )
        btn_volver.pack(side="right")

        # ── Panel de contenido ─────────────────────────────────────────
        self._content_panel = tk.Frame(self, bg=self._bg)
        self._content_panel.pack(fill="both", expand=True, padx=Spacing.XS, pady=(6, 0))

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
        btn.config(bg=get_module_colors(_MODULE)["light"])

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

        for child in self._content_panel.winfo_children():
            child.pack_forget()

        if key not in self._loaded_views:
            try:
                view = self._build_tab_view(key)
                if view:
                    self._loaded_views[key] = view
            except Exception as exc:
                logger.exception("Error al cargar tab '%s': %s", key, exc)
                return

        view = self._loaded_views.get(key)
        if view:
            view.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Sub-vistas por tab
    # ------------------------------------------------------------------

    def _build_tab_view(self, key):
        parent = self._content_panel

        if key == "lista":
            from manager.app.ui.views.tenants_view import TenantsView
            return TenantsView(
                parent,
                on_navigate=self._on_navigate_from_list,
                on_data_change=self._on_data_change,
                on_register_payment=self.on_register_payment,
                on_new_tenant=lambda: self._select_tab("nuevo"),
            )

        if key == "nuevo":
            from manager.app.ui.views.tenant_form_view import TenantFormView
            return TenantFormView(
                parent,
                on_back=self._on_cancel_nuevo,
                on_save_success=self._on_tenant_saved,
                on_navigate_to_dashboard=self._go_to_dashboard,
            )

        if key == "inactivos":
            from manager.app.ui.views.inactive_tenants_view import InactiveTenantsView
            return InactiveTenantsView(
                parent,
                on_data_change=self._on_data_change,
            )

        if key == "reportes":
            from manager.app.ui.views.tenant_management_reports_view import TenantManagementReportsView
            return TenantManagementReportsView(
                parent,
                on_back=None,
                on_navigate=self._go_to_dashboard,
            )

        return None

    # ------------------------------------------------------------------
    # Navegación interna
    # ------------------------------------------------------------------

    def _on_navigate_from_list(self, destination):
        """Callback on_navigate que recibe TenantsView. Solo 'dashboard' es relevante."""
        if destination == "dashboard":
            self._go_to_dashboard()

    def _on_data_change(self):
        """Propaga cambios de datos al exterior y refresca la lista."""
        if self.on_data_change:
            self.on_data_change()
        # Invalidar caché de la lista y de inactivos para que recarguen al volver
        self._loaded_views.pop("lista", None)
        self._loaded_views.pop("inactivos", None)

    def _on_tenant_saved(self):
        """Tras guardar un nuevo inquilino: notifica cambios y vuelve a la lista."""
        self._loaded_views.pop("lista", None)
        self._loaded_views.pop("nuevo", None)
        if self.on_data_change:
            self.on_data_change()
        self._select_tab("lista")

    def _on_cancel_nuevo(self):
        """Cancela el formulario de nuevo inquilino y vuelve a la lista."""
        self._loaded_views.pop("nuevo", None)
        self._select_tab("lista")

    def _on_volver(self):
        """Back inteligente: delega a la vista activa si tiene navegación interna,
        si no hay nada que deshacer vuelve al dashboard."""
        view = self._loaded_views.get(self._active_tab)
        if view and hasattr(view, "go_back") and view.go_back():
            return  # la vista manejó el back internamente
        # No hay sub-vista activa: salir al dashboard
        self._go_to_dashboard()

    def _go_to_dashboard(self):
        if self.on_back:
            self.on_back()

    # ------------------------------------------------------------------
    # API pública (compatibilidad con main_window)
    # ------------------------------------------------------------------

    def select_tab(self, key: str):
        """Permite a main_window seleccionar un tab programáticamente."""
        self._select_tab(key)

    def refresh_list(self):
        """Refresca la lista de inquilinos si está cargada."""
        self._loaded_views.pop("lista", None)
        if self._active_tab == "lista":
            self._select_tab("lista")
