"""
Vista del dashboard: métricas y acciones principales.
Usa DashboardPresenter para los datos y recibe callbacks para las acciones.
"""

import tkinter as tk
from typing import Callable, Optional

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import (
    ModernSeparator,
    ModernMetricCard,
    DetailedMetricCard,
    get_module_colors,
)
from manager.app.presenters.dashboard_presenter import DashboardPresenter


class DashboardView(tk.Frame):
    """Vista del dashboard: métricas (inquilinos, pagos, ingresos, gastos, saldo) y grid de acciones."""

    def __init__(
        self,
        parent,
        presenter: Optional[DashboardPresenter] = None,
        on_new_tenant: Optional[Callable[[], None]] = None,
        on_register_expense: Optional[Callable[[], None]] = None,
        on_register_payment: Optional[Callable[[], None]] = None,
        on_search: Optional[Callable[[], None]] = None,
        on_occupation_status: Optional[Callable[[], None]] = None,
        on_pending_payments: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self._presenter = presenter or DashboardPresenter()
        self._on_new_tenant = on_new_tenant
        self._on_register_expense = on_register_expense
        self._on_register_payment = on_register_payment
        self._on_search = on_search
        self._on_occupation_status = on_occupation_status
        self._on_pending_payments = on_pending_payments
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg_content = theme.get("content_bg", "#f8fafc")
        self.configure(bg=self._bg_content)
        self._build_ui()

    def _build_ui(self):
        self._build_metrics_row()
        ModernSeparator(self)
        self._build_actions_grid()

    def _build_metrics_row(self):
        metrics_frame = tk.Frame(self, bg=self._bg_content)
        metrics_frame.pack(fill="x", pady=(0, Spacing.XL))
        metrics_row = tk.Frame(metrics_frame, bg=self._bg_content)
        metrics_row.pack(fill="x")

        tenant_stats = self._presenter.get_tenant_statistics()
        inactivos = tenant_stats.get("inactivo", 0)
        total_activos = tenant_stats["total"] - inactivos

        metric1 = DetailedMetricCard(
            metrics_row,
            title="Total Inquilinos",
            total_value=str(total_activos),
            details=[
                {"label": "Al día", "value": tenant_stats["al_dia"], "color": "#10b981"},
                {"label": "En mora", "value": tenant_stats["moroso"], "color": "#ef4444"},
            ],
            icon=Icons.TENANTS,
            color_theme="primary",
        )
        metric1.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        pagos_pendientes = self._presenter.get_pending_payments_total()
        metric2 = ModernMetricCard(
            metrics_row,
            title="Pagos Pendientes",
            value=f"${int(pagos_pendientes):,}",
            icon=Icons.PAYMENT_PENDING,
            color_theme="warning",
        )
        metric2.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        ingresos_mes = self._presenter.get_payments_of_current_month()
        metric3 = ModernMetricCard(
            metrics_row,
            title="Ingresos del Mes",
            value=f"${int(ingresos_mes):,}",
            icon=Icons.PAYMENT_RECEIVED,
            color_theme="success",
        )
        metric3.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        gastos_mes = self._presenter.get_expenses_of_current_month()
        metric4 = ModernMetricCard(
            metrics_row,
            title="Gastos del Mes",
            value=f"${int(gastos_mes):,}",
            icon=Icons.EXPENSES,
            color_theme="error",
        )
        metric4.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        saldo_neto = ingresos_mes - gastos_mes
        if saldo_neto >= 0:
            net_value = f"${int(saldo_neto):,}"
            net_theme = "success"
        else:
            net_value = f"-${int(abs(saldo_neto)):,}"
            net_theme = "error"
        metric5 = ModernMetricCard(
            metrics_row,
            title="Saldo Neto del Mes",
            value=net_value,
            icon="💼",
            color_theme=net_theme,
        )
        metric5.pack(side="left", fill="both", expand=True)

    def _build_actions_grid(self):
        main_container = tk.Frame(self, bg=self._bg_content)
        main_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        actions_block = tk.Frame(main_container, bg=self._bg_content)
        actions_block.pack(anchor="center", expand=True)

        title_label = tk.Label(
            actions_block,
            text="Acciones Principales",
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            bg=self._bg_content,
            font=("Segoe UI", 18, "bold"),
            anchor="center",
        )
        title_label.pack(fill="x", pady=(0, Spacing.SM))

        grid_container = tk.Frame(actions_block, bg=self._bg_content)
        grid_container.pack(fill="both", expand=True)
        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(2):
            grid_container.grid_rowconfigure(i, weight=1, uniform="row")

        cards_data = [
            {
                "icon": "👤", "title": "Nuevo Inquilino",
                "description": "", "color": "#1e40af", "module": "inquilinos",
                "action": self._on_new_tenant, "row": 0, "col": 0,
            },
            {
                "icon": "💸", "title": "Registrar Gasto",
                "description": "", "color": "#991b1b", "module": "gastos",
                "action": self._on_register_expense, "row": 0, "col": 1,
            },
            {
                "icon": "💰", "title": "Registrar Pago",
                "description": "", "color": "#166534", "module": "pagos",
                "action": self._on_register_payment, "row": 0, "col": 2,
            },
            {
                "icon": "🔍", "title": "Buscar Inquilino",
                "description": "", "color": "#1e40af", "module": "inquilinos",
                "action": self._on_search, "row": 1, "col": 0,
            },
            {
                "icon": "🏠", "title": "Estado de Ocupación",
                "description": "", "color": "#6d28d9", "module": "administración",
                "action": self._on_occupation_status, "row": 1, "col": 1,
            },
            {
                "icon": "⏰", "title": "Pagos Pendientes",
                "description": "", "color": "#166534", "module": "pagos",
                "action": self._on_pending_payments, "row": 1, "col": 2,
            },
        ]

        for card_info in cards_data:
            action = card_info["action"]
            if not callable(action):
                continue
            card = self._create_action_card(
                grid_container,
                card_info["icon"],
                card_info["title"],
                card_info["color"],
                action,
                module=card_info.get("module"),
            )
            card.grid(
                row=card_info["row"],
                column=card_info["col"],
                sticky="nsew",
                padx=Spacing.SM,
                pady=Spacing.SM,
            )

    def _create_action_card(self, parent, icon: str, title: str, color: str, action: Callable, module: Optional[str] = None):
        """Card de acción con fondo por módulo y hover."""
        if module:
            colors = get_module_colors(module)
            dashboard_bg = colors["light"]
            hover_map = {
                "inquilinos": "#93c5fd",
                "pagos": "#86efac",
                "gastos": "#fca5a5",
                "administración": "#d8b4fe",
                "reportes": "#fdba74",
            }
            dashboard_hover = hover_map.get(module, "#d8b4fe")
        else:
            dashboard_bg = "#f3e8ff"
            dashboard_hover = "#e9d5ff"

        card = tk.Frame(parent, bg=dashboard_bg, bd=2, relief="raised", width=280, height=220)
        card.pack_propagate(False)
        card.configure(cursor="hand2")

        content_frame = tk.Frame(card, bg=dashboard_bg)
        content_frame.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        content_container = tk.Frame(content_frame, bg=dashboard_bg)
        content_container.pack(anchor="center", pady=(Spacing.SM, 0))

        icon_label = tk.Label(
            content_container, text=icon, font=("Segoe UI Symbol", 26),
            fg=color, bg=dashboard_bg,
        )
        icon_label.pack(pady=(0, Spacing.XS))
        title_label = tk.Label(
            content_container, text=title, font=("Segoe UI", 13, "bold"),
            fg="#000000", bg=dashboard_bg, wraplength=240, justify="center",
        )
        title_label.pack()

        def on_card_click(e):
            e.widget.focus_set()
            action()
            return "break"

        def on_enter(e):
            card.configure(bg=dashboard_hover)
            content_frame.configure(bg=dashboard_hover)
            content_container.configure(bg=dashboard_hover)
            icon_label.configure(bg=dashboard_hover)
            title_label.configure(bg=dashboard_hover)

        def on_leave(e):
            def _check_leave():
                try:
                    root = card.winfo_toplevel()
                    root.update_idletasks()
                    x, y = root.winfo_pointerx(), root.winfo_pointery()
                    w = root.winfo_containing(x, y)
                    cur = w
                    while cur:
                        if cur == card:
                            return
                        try:
                            cur = cur.master
                        except (tk.TclError, AttributeError):
                            break
                except (tk.TclError, AttributeError):
                    pass
                card.configure(bg=dashboard_bg)
                content_frame.configure(bg=dashboard_bg)
                content_container.configure(bg=dashboard_bg)
                icon_label.configure(bg=dashboard_bg)
                title_label.configure(bg=dashboard_bg)
            card.after(10, _check_leave)

        for widget in (card, content_frame, content_container, icon_label, title_label):
            widget.bind("<Button-1>", on_card_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        return card
