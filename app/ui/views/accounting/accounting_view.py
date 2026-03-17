"""
Vista hub principal del módulo de contabilidad.
Layout: fila de tabs en la parte superior + panel de contenido inferior.
Lazy load: cada sub-vista se instancia la primera vez que se selecciona su tab.
"""
import tkinter as tk

from manager.app.ui.components.theme_manager import Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.presenters.accounting_presenter import AccountingPresenter
from manager.app.logger import logger


# Definición de tabs: (clave, icono, etiqueta, clase)
_TABS = [
    ("ledger",   "📒", "Libro de movimientos"),
    ("opening",  "📂", "Asientos de apertura"),
    ("manual",   "✏️",  "Asientos manuales"),
    ("income",   "📊", "Estado de resultados"),
]


class AccountingView(tk.Frame):
    """Hub principal del módulo de contabilidad con tabs de navegación."""

    def __init__(self, parent, on_back=None, on_navigate_to_dashboard=None):
        super().__init__(parent)
        self.configure(bg=parent.cget("bg"))
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.presenter = AccountingPresenter(
            on_back=on_back,
            on_navigate_to_dashboard=on_navigate_to_dashboard,
        )

        self._active_tab = None
        self._tab_buttons = {}   # clave → botón tab
        self._loaded_views = {}  # clave → instancia de sub-vista (lazy)

        self._build_layout()
        self._select_tab("ledger")  # tab inicial

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        bg = self.cget("bg")
        colors = get_module_colors("contabilidad")

        # --- Fila única: tabs a la izquierda + Dashboard a la derecha ---
        top_bar = tk.Frame(self, bg=bg)
        top_bar.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, Spacing.SM))

        # Dashboard a la derecha
        btn = create_rounded_button(
            top_bar,
            text="🏠 Dashboard",
            bg_color=colors["primary"],
            fg_color="white",
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._go_to_dashboard,
            padx=14,
            pady=6,
            radius=4,
            border_color="#000000",
        )
        btn.pack(side="right")

        # Tabs a la izquierda, en la misma fila
        self._tabs_bar = tk.Frame(top_bar, bg=bg)
        self._tabs_bar.pack(side="left", fill="x")

        for key, icon, label in _TABS:
            self._create_tab_button(self._tabs_bar, key, icon, label)

        # --- Panel de contenido (ocupa el resto) ---
        self._content_panel = tk.Frame(self, bg=bg)
        self._content_panel.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.SM))

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _create_tab_button(self, parent, key, icon, label):
        colors = get_module_colors("contabilidad")
        bg_inactive = "#ccfbf1"   # teal-100
        fg_inactive = "#0f766e"   # teal-700

        btn_frame = tk.Frame(parent, bg=self.cget("bg"))
        btn_frame.pack(side="left", padx=(0, Spacing.SM))

        btn = tk.Label(
            btn_frame,
            text=f"{icon}  {label}",
            font=("Segoe UI", 10, "bold"),
            bg=bg_inactive,
            fg=fg_inactive,
            padx=12,
            pady=6,
            cursor="hand2",
            relief="flat",
        )
        btn.pack()

        def on_click(e, k=key):
            self._select_tab(k)

        def on_enter(e, b=btn, k=key):
            if k != self._active_tab:
                b.configure(bg="#99f6e4")  # teal-200 hover

        def on_leave(e, b=btn, k=key):
            if k != self._active_tab:
                b.configure(bg=bg_inactive)

        btn.bind("<Button-1>", on_click)
        btn.bind("<Enter>",    on_enter)
        btn.bind("<Leave>",    on_leave)

        self._tab_buttons[key] = btn

    def _select_tab(self, key):
        colors = get_module_colors("contabilidad")
        bg_inactive = "#ccfbf1"
        fg_inactive = "#0f766e"
        bg_active   = colors["primary"]   # teal-700
        fg_active   = "white"

        # Actualizar estilos de todos los tabs
        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.configure(bg=bg_active, fg=fg_active)
            else:
                btn.configure(bg=bg_inactive, fg=fg_inactive)

        self._active_tab = key
        self._show_content(key)

    # ------------------------------------------------------------------
    # Contenido (lazy load)
    # ------------------------------------------------------------------

    def _show_content(self, key):
        # Ocultar todas las sub-vistas cargadas
        for view in self._loaded_views.values():
            view.pack_forget()

        # Instanciar si aún no existe
        if key not in self._loaded_views:
            view = self._build_subview(key)
            if view is None:
                return
            self._loaded_views[key] = view

        self._loaded_views[key].pack(fill="both", expand=True)

    def _build_subview(self, key):
        parent = self._content_panel
        try:
            if key == "ledger":
                from .ledger_view import LedgerView
                return LedgerView(parent, on_back=None)
            elif key == "opening":
                from .opening_entry_view import OpeningEntryView
                return OpeningEntryView(parent, on_back=None)
            elif key == "manual":
                from .manual_entry_view import ManualEntryView
                return ManualEntryView(parent, on_back=None)
            elif key == "income":
                from .income_statement_view import IncomeStatementView
                return IncomeStatementView(parent, on_back=None)
        except Exception as exc:
            logger.exception("Error al cargar sub-vista '%s': %s", key, exc)
            import tkinter.messagebox as mb
            mb.showerror("Error", f"No se pudo cargar la sección:\n{exc}")
            return None

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def _go_to_dashboard(self):
        if self.on_navigate_to_dashboard:
            self.on_navigate_to_dashboard()
        elif self.on_back:
            self.on_back()
