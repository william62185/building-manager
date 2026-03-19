"""
Vista hub principal del módulo de contabilidad.
Layout: barra de tabs anclada (fondo diferenciado + borde inferior) + panel de contenido.
Lazy load: cada sub-vista se instancia la primera vez que se selecciona su tab.
"""
import tkinter as tk

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.presenters.accounting_presenter import AccountingPresenter
from manager.app.logger import logger

_TABS = [
    ("ledger",  "📒", "Libro de movimientos"),
    ("opening", "", "Asientos de apertura"),
    ("manual",  "✏️",  "Asientos manuales"),
    ("income",  "📊", "Estado de resultados"),
]

_MODULE         = "contabilidad"
_TAB_BAR_BG     = "#e8ecf0"
_TAB_BAR_BORDER = "#c5cdd6"


class AccountingView(tk.Frame):
    """Hub principal del módulo de contabilidad con tabs de navegación."""

    def __init__(self, parent, on_back=None, on_navigate_to_dashboard=None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.presenter = AccountingPresenter(
            on_back=on_back,
            on_navigate_to_dashboard=on_navigate_to_dashboard,
        )

        self._active_tab = None
        self._tab_buttons = {}
        self._loaded_views = {}

        self._build_layout()
        self._select_tab("ledger")

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

        # Tabs a la izquierda
        tabs_left = tk.Frame(self._tab_bar, bg=_TAB_BAR_BG)
        tabs_left.pack(side="left", fill="y")

        for key, icon, label in _TABS:
            self._create_tab_button(tabs_left, key, icon, label)

        # Botones a la derecha: Volver + Inicio
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
                view = self._build_subview(key)
                if view:
                    self._loaded_views[key] = view
            except Exception as exc:
                logger.exception("Error al cargar tab '%s': %s", key, exc)
                return

        view = self._loaded_views.get(key)
        if view:
            view.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Sub-vistas (lazy load)
    # ------------------------------------------------------------------

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

    def _on_volver(self):
        """Recarga el tab activo descartando la vista cacheada."""
        if self._active_tab:
            self._loaded_views.pop(self._active_tab, None)
            self._select_tab(self._active_tab)

    def _go_to_dashboard(self):
        if self.on_navigate_to_dashboard:
            self.on_navigate_to_dashboard()
        elif self.on_back:
            self.on_back()
