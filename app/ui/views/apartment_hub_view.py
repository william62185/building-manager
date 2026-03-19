"""
Hub principal del módulo de Gestión de Apartamentos.
Layout: barra de tabs anclada + panel de contenido (lazy load).

Tabs:
  - ocupacion  → OccupationStatusView
  - lista      → ApartmentsListView
  - registrar  → ApartmentFormView
  - reportes   → OccupancyVacancyReportView
"""
import tkinter as tk
from typing import Callable, Optional

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.logger import logger

_TABS = [
    ("ocupacion", "🏠", "Estado de Ocupación"),
]

_MODULE         = "administración"
_TAB_BAR_BG     = "#e8ecf0"
_TAB_BAR_BORDER = "#c5cdd6"


class ApartmentHubView(tk.Frame):
    """Hub principal del módulo de Gestión de Apartamentos con tabs de navegación."""

    def __init__(
        self,
        parent,
        on_back: Callable = None,
        on_data_change: Callable = None,
        initial_tab: str = "ocupacion",
    ):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)

        self.on_back = on_back
        self.on_data_change = on_data_change
        self._initial_tab = initial_tab

        self._active_tab: Optional[str] = None
        self._tab_buttons: dict = {}
        self._loaded_views: dict = {}

        self._build_layout()
        self.after(0, lambda: self._select_tab(self._initial_tab))

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
        self._content_panel.pack(fill="both", expand=True, padx=Spacing.XS, pady=0)

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

        if key == "ocupacion":
            from manager.app.ui.views.occupation_status_view import OccupationStatusView
            return OccupationStatusView(
                parent,
                on_back=self._go_to_dashboard,
                on_navigate=self._go_to_dashboard,
            )

        if key == "lista":
            from manager.app.ui.views.apartments_list_view import ApartmentsListView
            return ApartmentsListView(
                parent,
                on_back=self._go_to_dashboard,
                on_edit=self._on_edit_apartment,
                on_navigate=self._go_to_dashboard,
                on_new=lambda: self._select_tab("registrar"),
            )

        if key == "registrar":
            from manager.app.ui.views.apartment_form_view import ApartmentFormView
            return ApartmentFormView(
                parent,
                on_back=lambda: self._select_tab("lista"),
                on_save_success=self._on_data_changed,
                apartment_data=None,
                on_navigate=self._go_to_dashboard,
            )

        if key == "reportes":
            from manager.app.ui.views.reports.occupancy_vacancy_report_view import OccupancyVacancyReportView
            return OccupancyVacancyReportView(
                parent,
                on_back=self._go_to_dashboard,
                on_navigate=self._go_to_dashboard,
            )

        return None

    # ------------------------------------------------------------------
    # Callbacks internos
    # ------------------------------------------------------------------

    def _on_edit_apartment(self, apartment_data: dict, filter_state: dict):
        """Abre el formulario de edición invalidando la caché del tab registrar."""
        self._loaded_views.pop("registrar", None)
        from manager.app.ui.views.apartment_form_view import ApartmentFormView
        parent = self._content_panel
        view = ApartmentFormView(
            parent,
            on_back=lambda: self._select_tab("lista"),
            on_save_success=self._on_data_changed,
            apartment_data=apartment_data,
            on_navigate=self._go_to_dashboard,
        )
        self._loaded_views["registrar"] = view
        self._select_tab("registrar")

    def _on_data_changed(self):
        """Invalida lista y ocupación para que recarguen al volver."""
        self._loaded_views.pop("lista", None)
        self._loaded_views.pop("ocupacion", None)
        self._loaded_views.pop("registrar", None)
        if self.on_data_change:
            self.on_data_change()
        self._select_tab("lista")

    def _on_volver(self):
        self._go_to_dashboard()

    def _go_to_dashboard(self):
        if self.on_back:
            self.on_back()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def select_tab(self, key: str):
        self._select_tab(key)
