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
        sep = tk.Frame(self, height=1, bg=theme_manager.themes[theme_manager.current_theme]["border_light"])
        sep.pack(fill="x")
        self._build_actions_grid()

    def _build_metrics_row(self):
        now = __import__("datetime").datetime.now()
        theme = theme_manager.themes[theme_manager.current_theme]
        card_bg = theme["bg_secondary"] if theme_manager.current_theme == "dark" else "white"
        border = theme["border_light"]

        metrics_frame = tk.Frame(self, bg=self._bg_content)
        metrics_frame.pack(fill="x", pady=(4, Spacing.SM))

        # ── Fila 1: métricas del mes ──────────────────────────────────────────
        row1_label = tk.Label(
            metrics_frame,
            text=f"Mes actual — {now.strftime('%B %Y').capitalize()}",
            font=("Segoe UI", 9, "bold"),
            bg=self._bg_content,
            fg="#374151",
            anchor="w",
        )
        row1_label.pack(fill="x", padx=2, pady=(0, 3))

        metrics_row1 = tk.Frame(metrics_frame, bg=self._bg_content)
        metrics_row1.pack(fill="x")

        tenant_stats = self._presenter.get_tenant_statistics()
        inactivos = tenant_stats.get("inactivo", 0)
        total_activos = tenant_stats["total"] - inactivos
        pendiente_pago = tenant_stats.get("pendiente_pago", 0)

        def _compact_card(parent, title, icon="", inline_value=""):
            """Card compacta para fila 1.
            Si inline_value se pasa, el valor se muestra en el header (misma línea que el título).
            Retorna (frame, value_label_o_None, details_frame).
            """
            f = tk.Frame(parent, bg=card_bg, relief="flat", bd=1,
                         highlightbackground=border, highlightthickness=1)
            inner = tk.Frame(f, bg=card_bg)
            inner.pack(fill="both", expand=True, padx=5, pady=4)
            hdr = tk.Frame(inner, bg=card_bg)
            hdr.pack(fill="x")
            if icon:
                tk.Label(hdr, text=icon, bg=card_bg, fg="#000",
                         font=("Segoe UI Symbol", 9)).pack(side="left", padx=(0, 3))
            tk.Label(hdr, text=title, bg=card_bg, fg="#000",
                     font=("Segoe UI", 8)).pack(side="left")
            val_lbl = None
            if inline_value:
                # Valor en el header, a la derecha del título
                val_lbl = tk.Label(hdr, text=inline_value, bg=card_bg,
                                   fg=theme["text_primary"], font=("Segoe UI", 11, "bold"))
                val_lbl.pack(side="right")
            else:
                # Valor en línea propia debajo del header
                val_lbl = tk.Label(inner, text="", bg=card_bg,
                                   fg=theme["text_primary"], font=("Segoe UI", 11, "bold"))
                val_lbl.pack(anchor="w", pady=(1, 0))
            det_frame = tk.Frame(inner, bg=card_bg)
            det_frame.pack(fill="x")
            return f, val_lbl, det_frame

        def _add_detail(parent, label, value, color):
            row = tk.Frame(parent, bg=card_bg)
            row.pack(fill="x")
            tk.Label(row, text=label, bg=card_bg, fg="#6b7280",
                     font=("Segoe UI", 8)).pack(side="left")
            tk.Label(row, text=str(value), bg=card_bg, fg=color,
                     font=("Segoe UI", 8, "bold")).pack(side="right")

        # Card 1 — Inquilinos (número inline junto al título)
        c1, v1, d1 = _compact_card(metrics_row1, "Total Inquilinos", Icons.TENANTS,
                                   inline_value=str(total_activos))
        _add_detail(d1, "Al día",      tenant_stats["al_dia"], "#10b981")
        _add_detail(d1, "Pend. pago",  pendiente_pago,         "#f59e0b")
        _add_detail(d1, "En mora",     tenant_stats["moroso"], "#ef4444")
        c1.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        # Card 2 — Ingresos del mes
        ingresos_mes = self._presenter.get_payments_of_current_month()
        c2, v2, _ = _compact_card(metrics_row1, "Ingresos del Mes", Icons.PAYMENT_RECEIVED)
        v2.config(text=f"${int(ingresos_mes):,}")
        c2.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        # Card 3 — Gastos del mes
        gastos_mes = self._presenter.get_expenses_of_current_month()
        c3, v3, _ = _compact_card(metrics_row1, "Gastos del Mes", Icons.EXPENSES)
        v3.config(text=f"${int(gastos_mes):,}")
        c3.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        # Card 4 — Saldo neto
        saldo_mes = ingresos_mes - gastos_mes
        c4, v4, _ = _compact_card(metrics_row1, "Saldo Neto del Mes", "💼")
        v4.config(
            text=f"${int(saldo_mes):,}" if saldo_mes >= 0 else f"-${int(abs(saldo_mes)):,}",
            fg="#10b981" if saldo_mes >= 0 else "#ef4444",
        )
        c4.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        # Card 5 — Ocupación
        ocup = self._presenter.get_occupation_rate()
        c5, v5, d5 = _compact_card(metrics_row1, "Ocupación", "🏠")
        v5.config(text=f"{ocup['rate']}%")
        _add_detail(d5, "Ocupados",    ocup["occupied"],                    "#10b981")
        _add_detail(d5, "Disponibles", ocup["total"] - ocup["occupied"],    "#6b7280")
        c5.pack(side="left", fill="both", expand=True)

        # ── Separador entre filas ─────────────────────────────────────────────
        sep = tk.Frame(metrics_frame, height=1, bg="#e5e7eb")
        sep.pack(fill="x", pady=(4, 3))

        # ── Fila 2: métricas anuales ──────────────────────────────────────────
        row2_label = tk.Label(
            metrics_frame,
            text=f"Año {now.year}",
            font=("Segoe UI", 9, "bold"),
            bg=self._bg_content,
            fg="#374151",
            anchor="w",
        )
        row2_label.pack(fill="x", padx=2, pady=(0, 4))

        metrics_row2 = tk.Frame(metrics_frame, bg=self._bg_content)
        metrics_row2.pack(fill="x")

        ingresos_anio = self._presenter.get_payments_of_current_year()
        a1 = ModernMetricCard(
            metrics_row2,
            title="Ingresos del Año",
            value=f"${int(ingresos_anio):,}",
            icon=Icons.PAYMENT_RECEIVED,
            color_theme="success",
        )
        a1.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        gastos_anio = self._presenter.get_expenses_of_current_year()
        a2 = ModernMetricCard(
            metrics_row2,
            title="Gastos del Año",
            value=f"${int(gastos_anio):,}",
            icon=Icons.EXPENSES,
            color_theme="error",
        )
        a2.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        saldo_anio = ingresos_anio - gastos_anio
        saldo_anio_color = "#10b981" if saldo_anio >= 0 else "#ef4444"
        a3 = ModernMetricCard(
            metrics_row2,
            title="Saldo Neto del Año",
            value=f"${int(saldo_anio):,}" if saldo_anio >= 0 else f"-${int(abs(saldo_anio)):,}",
            icon="💼",
            color_theme="success" if saldo_anio >= 0 else "error",
            value_color=saldo_anio_color,
        )
        a3.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        pagos_pendientes = self._presenter.get_pending_payments_total()
        a4 = ModernMetricCard(
            metrics_row2,
            title="Pagos Pendientes",
            value=f"${int(pagos_pendientes):,}",
            icon=Icons.PAYMENT_PENDING,
            color_theme="warning",
            warning_highlight=pagos_pendientes > 0,
        )
        a4.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))

        promedio = self._presenter.get_monthly_income_average()
        a5 = ModernMetricCard(
            metrics_row2,
            title="Promedio Mensual",
            value=f"${int(promedio):,}",
            icon="📊",
            color_theme="primary",
        )
        a5.pack(side="left", fill="both", expand=True)

    def _build_actions_grid(self):
        main_container = tk.Frame(self, bg=self._bg_content)
        main_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, 4))
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
