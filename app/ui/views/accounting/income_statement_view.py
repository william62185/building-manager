"""
Vista Estado de resultados del módulo de contabilidad.
Selector de período + panel de resultados con secciones
de ingresos, egresos por categoría, ajustes y balance neto.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from calendar import monthrange

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import get_module_colors, bind_combobox_dropdown_on_click
from manager.app.ui.views.register_expense_view import DatePickerWidget
from manager.app.presenters.accounting_presenter import AccountingPresenter
from manager.app.logger import logger

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


class IncomeStatementView(tk.Frame):
    """Vista del Estado de resultados con selector de período y panel de resultados."""

    def __init__(self, parent, on_back=None, presenter=None):
        super().__init__(parent)
        self.configure(bg=parent.cget("bg"))
        self._bg = parent.cget("bg")
        self.on_back = on_back
        self._colors = get_module_colors("contabilidad")
        self.presenter = presenter if presenter else AccountingPresenter()
        self._last_data = None
        self._last_period_label = ""

        self._build_layout()
        self._generate()

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        bg = self._bg
        teal = self._colors["primary"]
        teal_hover = self._colors["hover"]
        theme = theme_manager.themes[theme_manager.current_theme]

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 9, current_year + 1)]
        years.reverse()

        # ── Fila superior: período + botones de acción ──────────────────
        top = tk.Frame(self, bg=bg)
        top.pack(fill="x", padx=Spacing.LG, pady=(4, 4))

        period_frame = tk.LabelFrame(
            top, text="Período",
            font=("Segoe UI", 9, "bold"),
            bg=bg, fg=theme["text_primary"],
            padx=6, pady=4,
        )
        period_frame.pack(side="left", fill="y")

        self._period_type = tk.StringVar(value="specific_month")

        # Fila 1: mes + año específico
        row1 = tk.Frame(period_frame, bg=bg)
        row1.pack(fill="x", pady=(0, 2))

        tk.Radiobutton(
            row1, text="Mes:", variable=self._period_type,
            value="specific_month", bg=bg, fg=theme["text_primary"],
            font=("Segoe UI", 9), activebackground=bg,
        ).pack(side="left")

        self._mes_var = tk.StringVar(value=MESES[datetime.now().month - 1])
        mes_combo = ttk.Combobox(
            row1, textvariable=self._mes_var,
            values=MESES, state="readonly", width=11,
        )
        mes_combo.pack(side="left", padx=(2, 4))
        bind_combobox_dropdown_on_click(mes_combo)
        mes_combo.bind("<<ComboboxSelected>>", lambda e: self._period_type.set("specific_month"))

        self._anio_var = tk.StringVar(value=str(current_year))
        anio_combo = ttk.Combobox(
            row1, textvariable=self._anio_var,
            values=years, state="readonly", width=7,
        )
        anio_combo.pack(side="left")
        bind_combobox_dropdown_on_click(anio_combo)
        anio_combo.bind("<<ComboboxSelected>>", lambda e: self._period_type.set("specific_month"))

        # Fila 2: año completo
        row2 = tk.Frame(period_frame, bg=bg)
        row2.pack(fill="x", pady=(0, 2))

        tk.Radiobutton(
            row2, text="Año:", variable=self._period_type,
            value="specific_year", bg=bg, fg=theme["text_primary"],
            font=("Segoe UI", 9), activebackground=bg,
        ).pack(side="left")

        self._anio_only_var = tk.StringVar(value=str(current_year))
        anio_only_combo = ttk.Combobox(
            row2, textvariable=self._anio_only_var,
            values=years, state="readonly", width=7,
        )
        anio_only_combo.pack(side="left", padx=(2, 0))
        bind_combobox_dropdown_on_click(anio_only_combo)
        anio_only_combo.bind("<<ComboboxSelected>>", lambda e: self._period_type.set("specific_year"))

        # Fila 3: rango personalizado
        row3 = tk.Frame(period_frame, bg=bg)
        row3.pack(fill="x")

        tk.Radiobutton(
            row3, text="Rango:", variable=self._period_type,
            value="custom", bg=bg, fg=theme["text_primary"],
            font=("Segoe UI", 9), activebackground=bg,
        ).pack(side="left")

        tk.Label(row3, text="Desde:", font=("Segoe UI", 8),
                 bg=bg, fg=theme["text_primary"]).pack(side="left", padx=(2, 1))
        self._date_from = DatePickerWidget(row3, on_change=lambda: self._period_type.set("custom"))
        self._date_from.pack(side="left", padx=(0, 4))

        tk.Label(row3, text="Hasta:", font=("Segoe UI", 8),
                 bg=bg, fg=theme["text_primary"]).pack(side="left", padx=(0, 1))
        self._date_to = DatePickerWidget(row3, on_change=lambda: self._period_type.set("custom"))
        self._date_to.pack(side="left")

        # ── Botones de acción (derecha del período) ─────────────────────
        btn_col = tk.Frame(top, bg=bg)
        btn_col.pack(side="left", padx=(8, 0), anchor="n")

        btn_gen = tk.Button(
            btn_col, text="⟳ Generar",
            font=("Segoe UI", 9, "bold"),
            bg=teal, fg="white", relief="flat", padx=10, pady=4,
            cursor="hand2", command=self._generate,
        )
        btn_gen.pack(fill="x", pady=(0, 3))
        btn_gen.bind("<Enter>", lambda e: btn_gen.config(bg=teal_hover))
        btn_gen.bind("<Leave>", lambda e: btn_gen.config(bg=teal))

        btn_csv = tk.Button(
            btn_col, text="↓ CSV",
            font=("Segoe UI", 9),
            bg="#475569", fg="white", relief="flat", padx=10, pady=3,
            cursor="hand2", command=lambda: self._export("csv"),
        )
        btn_csv.pack(fill="x", pady=(0, 3))
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg="#334155"))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg="#475569"))

        btn_txt = tk.Button(
            btn_col, text="↓ TXT",
            font=("Segoe UI", 9),
            bg="#475569", fg="white", relief="flat", padx=10, pady=3,
            cursor="hand2", command=lambda: self._export("txt"),
        )
        btn_txt.pack(fill="x")
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg="#334155"))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg="#475569"))

        # ── Panel de resultados (sin scroll) ────────────────────────────
        self._results_frame = tk.Frame(self, bg=bg)
        self._results_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(4, 4))

    # ------------------------------------------------------------------
    # Resolución de período
    # ------------------------------------------------------------------

    def _resolve_period(self):
        period = self._period_type.get()

        if period == "specific_month":
            mes_nombre = self._mes_var.get()
            anio_str = self._anio_var.get()
            if not mes_nombre or not anio_str:
                return None, None, None
            anio = int(anio_str)
            mes_num = MESES.index(mes_nombre) + 1
            ultimo_dia = monthrange(anio, mes_num)[1]
            date_from = f"{anio:04d}-{mes_num:02d}-01"
            date_to = f"{anio:04d}-{mes_num:02d}-{ultimo_dia:02d}"
            return date_from, date_to, f"{mes_nombre} {anio_str}"

        if period == "specific_year":
            anio_str = self._anio_only_var.get()
            if not anio_str:
                return None, None, None
            return f"{anio_str}-01-01", f"{anio_str}-12-31", f"Año {anio_str}"

        if period == "custom":
            df = self._date_from.get().strip()
            dt = self._date_to.get().strip()
            if not df or not dt:
                return None, None, None
            try:
                df_obj = datetime.strptime(df, "%d/%m/%Y")
                dt_obj = datetime.strptime(dt, "%d/%m/%Y")
                if df_obj > dt_obj:
                    return None, None, None
                return (
                    df_obj.strftime("%Y-%m-%d"),
                    dt_obj.strftime("%Y-%m-%d"),
                    f"{df} a {dt}",
                )
            except ValueError:
                return None, None, None

        return None, None, None

    # ------------------------------------------------------------------
    # Generación del estado de resultados
    # ------------------------------------------------------------------

    def _generate(self):
        date_from, date_to, period_label = self._resolve_period()
        if date_from is None:
            messagebox.showwarning(
                "Período inválido",
                "Seleccione un período válido e intente de nuevo.",
            )
            return

        try:
            data = self.presenter.get_income_statement(date_from, date_to)
            self._last_data = data
            self._last_period_label = period_label
            self._render_results(data, period_label)
        except Exception as exc:
            logger.exception("Error al generar estado de resultados: %s", exc)
            messagebox.showerror("Error", f"No se pudo generar el estado de resultados:\n{exc}")

    def _render_results(self, data: dict, period_label: str):
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]
        sep_color = theme.get("border_light", "#e0e0e0")

        for w in self._results_frame.winfo_children():
            w.destroy()

        def section_title(parent, text):
            tk.Label(
                parent, text=text,
                font=("Segoe UI", 10, "bold"),
                bg=bg, fg=theme["text_primary"], anchor="w",
            ).pack(fill="x", pady=(6, 1))
            tk.Frame(parent, height=1, bg=sep_color).pack(fill="x", pady=(0, 2))

        def data_row(parent, label, value, bold=False, color=None):
            row = tk.Frame(parent, bg=bg)
            row.pack(fill="x", pady=1)
            font = ("Segoe UI", 9, "bold") if bold else ("Segoe UI", 9)
            tk.Label(row, text=label, font=font, bg=bg,
                     fg=color or theme["text_primary"], anchor="w").pack(side="left")
            tk.Label(row, text=f"${value:,.2f}", font=font, bg=bg,
                     fg=color or theme["text_primary"], anchor="e").pack(side="right")

        # Título
        tk.Label(
            self._results_frame,
            text=f"Estado de Resultados — {period_label}",
            font=("Segoe UI", 11, "bold"),
            bg=bg, fg=theme["text_primary"],
        ).pack(anchor="w", pady=(0, 4))

        # Todo en una sola columna (izquierda → abajo)
        col = tk.Frame(self._results_frame, bg=bg)
        col.pack(fill="both", expand=True)

        # Ingresos
        section_title(col, "INGRESOS")
        ingresos = data.get("ingresos_arriendo", 0.0)
        data_row(col, "Ingresos por arriendo", ingresos)
        data_row(col, "Total ingresos", ingresos, bold=True)

        # Egresos
        section_title(col, "EGRESOS POR CATEGORÍA")
        egresos_cat = data.get("egresos_por_categoria", {})
        if egresos_cat:
            for cat, monto in egresos_cat.items():
                data_row(col, cat, monto)
        else:
            tk.Label(
                col, text="Sin egresos en el período.",
                font=("Segoe UI", 9), bg=bg,
                fg=theme.get("text_secondary", "#6b7280"), anchor="w",
            ).pack(fill="x", pady=1)
        total_egresos = sum(egresos_cat.values()) if egresos_cat else 0.0
        data_row(col, "Total egresos", total_egresos, bold=True)

        # Ajustes
        section_title(col, "AJUSTES")
        ajustes = data.get("ajustes_netos", 0.0)
        data_row(col, "Ajustes netos", ajustes)

        # Balance neto
        section_title(col, "BALANCE NETO")
        balance = data.get("balance_neto", 0.0)
        balance_color = "#166534" if balance >= 0 else "#991b1b"
        balance_text = "Utilidad" if balance >= 0 else "Déficit"
        data_row(col, balance_text, balance, bold=True, color=balance_color)

        if balance == 0:
            tk.Label(
                col,
                text="Sin movimientos en el período.",
                font=("Segoe UI", 8),
                bg=bg, fg=theme.get("text_secondary", "#6b7280"),
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

    # ------------------------------------------------------------------
    # Exportación
    # ------------------------------------------------------------------

    def _export(self, fmt: str):
        if self._last_data is None:
            messagebox.showinfo("Sin datos", "Primero genere el estado de resultados.")
            return
        try:
            path = self.presenter.export_income_statement(
                self._last_data, fmt, self._last_period_label
            )
            messagebox.showinfo(
                "Exportación exitosa",
                f"Archivo generado correctamente:\n{path}",
            )
        except Exception as exc:
            logger.exception("Error al exportar estado de resultados: %s", exc)
            messagebox.showerror("Error al exportar", f"No se pudo exportar el archivo:\n{exc}")
