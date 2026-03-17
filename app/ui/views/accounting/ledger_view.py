"""
Vista del Libro de movimientos del módulo de contabilidad.
Muestra movimientos consolidados con filtros por período y tipo,
exportación a CSV/TXT y resumen de totales en el footer.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from calendar import monthrange

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import get_module_colors, bind_combobox_dropdown_on_click
from manager.app.presenters.accounting_presenter import AccountingPresenter
from manager.app.logger import logger

# Meses en español
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

# Colores de fila por tipo de movimiento
ROW_COLORS = {
    "ingreso":       "#dcfce7",   # verde claro
    "egreso":        "#fee2e2",   # rojo claro
    "ajuste":        "#ccfbf1",   # teal claro
    "ajuste_entrada": "#dcfce7",  # verde claro (ajuste de entrada = ingreso)
    "ajuste_salida":  "#fee2e2",  # rojo claro  (ajuste de salida  = egreso)
}


class LedgerView(tk.Frame):
    """Vista del Libro de movimientos con filtros, tabla y footer de totales."""

    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.configure(bg=parent.cget("bg"))
        self._bg = parent.cget("bg")
        self.on_back = on_back
        self.presenter = AccountingPresenter()
        self._colors = get_module_colors("contabilidad")
        self._movements = []

        self._build_layout()
        self._load_movements()

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        """Construye el layout de dos zonas: filtros (izquierda) y tabla (derecha)."""
        bg = self._bg

        outer = tk.Frame(self, bg=bg)
        outer.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)

        # Panel izquierdo — filtros (ancho fijo ~280px)
        self._filter_panel = tk.Frame(outer, bg=bg, width=280)
        self._filter_panel.pack(side="left", fill="y", padx=(0, Spacing.MD))
        self._filter_panel.pack_propagate(False)
        self._build_filter_panel(self._filter_panel)

        # Panel derecho — tabla + footer
        right_panel = tk.Frame(outer, bg=bg)
        right_panel.pack(side="left", fill="both", expand=True)
        self._build_right_panel(right_panel)

    # ------------------------------------------------------------------
    # Panel de filtros
    # ------------------------------------------------------------------

    def _build_filter_panel(self, parent):
        """Construye el panel de filtros en el lado izquierdo."""
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]
        teal = self._colors["primary"]

        tk.Label(
            parent,
            text="Filtros",
            font=("Segoe UI", 12, "bold"),
            bg=bg,
            fg=theme["text_primary"],
        ).pack(anchor="w", pady=(0, Spacing.SM))

        # --- Mes ---
        tk.Label(parent, text="Mes:", font=("Segoe UI", 10), bg=bg,
                 fg=theme["text_primary"]).pack(anchor="w")
        self._mes_var = tk.StringVar(value=MESES[datetime.now().month - 1])
        mes_combo = ttk.Combobox(
            parent, textvariable=self._mes_var,
            values=["Todos"] + MESES, state="readonly", width=22,
        )
        mes_combo.pack(anchor="w", pady=(0, Spacing.SM))
        bind_combobox_dropdown_on_click(mes_combo)

        # --- Año ---
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 4, current_year + 1)]
        years.reverse()

        tk.Label(parent, text="Año:", font=("Segoe UI", 10), bg=bg,
                 fg=theme["text_primary"]).pack(anchor="w")
        self._anio_var = tk.StringVar(value=str(current_year))
        anio_combo = ttk.Combobox(
            parent, textvariable=self._anio_var,
            values=years, state="readonly", width=22,
        )
        anio_combo.pack(anchor="w", pady=(0, Spacing.SM))
        bind_combobox_dropdown_on_click(anio_combo)

        # --- Tipo ---
        tk.Label(parent, text="Tipo:", font=("Segoe UI", 10), bg=bg,
                 fg=theme["text_primary"]).pack(anchor="w")
        self._tipo_var = tk.StringVar(value="Todos")
        tipo_combo = ttk.Combobox(
            parent, textvariable=self._tipo_var,
            values=["Todos", "Ingreso", "Egreso", "Ajuste"],
            state="readonly", width=22,
        )
        tipo_combo.pack(anchor="w", pady=(0, Spacing.MD))
        bind_combobox_dropdown_on_click(tipo_combo)

        # --- Separador ---
        tk.Frame(parent, height=1, bg=theme.get("border_light", "#e0e0e0")).pack(
            fill="x", pady=(0, Spacing.MD)
        )

        # --- Botón Aplicar ---
        btn_apply = tk.Button(
            parent,
            text="Aplicar filtros",
            font=("Segoe UI", 10, "bold"),
            bg=teal,
            fg="white",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._load_movements,
        )
        btn_apply.pack(fill="x", pady=(0, Spacing.SM))
        btn_apply.bind("<Enter>", lambda e: btn_apply.config(bg=self._colors["hover"]))
        btn_apply.bind("<Leave>", lambda e: btn_apply.config(bg=teal))

        # --- Botón Limpiar ---
        btn_clear = tk.Button(
            parent,
            text="Limpiar filtros",
            font=("Segoe UI", 10),
            bg="#6b7280",
            fg="white",
            relief="flat",
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._clear_filters,
        )
        btn_clear.pack(fill="x")
        btn_clear.bind("<Enter>", lambda e: btn_clear.config(bg="#4b5563"))
        btn_clear.bind("<Leave>", lambda e: btn_clear.config(bg="#6b7280"))

    # ------------------------------------------------------------------
    # Panel derecho: header de botones + tabla + footer
    # ------------------------------------------------------------------

    def _build_right_panel(self, parent):
        """Construye el panel derecho con header de botones, tabla y footer."""
        bg = self._bg

        # Header con botones de acción
        header = tk.Frame(parent, bg=bg)
        header.pack(fill="x", pady=(0, Spacing.SM))
        self._build_header_buttons(header)

        # Tabla (Treeview + scrollbar)
        table_frame = tk.Frame(parent, bg=bg)
        table_frame.pack(fill="both", expand=True)
        self._build_table(table_frame)

        # Footer de totales
        footer = tk.Frame(parent, bg=bg)
        footer.pack(fill="x", pady=(Spacing.SM, 0))
        self._build_footer(footer)

    def _build_header_buttons(self, parent):
        """Crea los botones Exportar CSV, Exportar TXT y × Volver."""
        bg = self._bg
        teal = self._colors["primary"]
        teal_hover = self._colors["hover"]

        btn_csv = tk.Button(
            parent,
            text="Exportar CSV",
            font=("Segoe UI", 10, "bold"),
            bg=teal, fg="white",
            relief="flat", padx=10, pady=6,
            cursor="hand2",
            command=lambda: self._export("csv"),
        )
        btn_csv.pack(side="left", padx=(0, Spacing.SM))
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=teal_hover))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=teal))

        btn_txt = tk.Button(
            parent,
            text="Exportar TXT",
            font=("Segoe UI", 10, "bold"),
            bg=teal, fg="white",
            relief="flat", padx=10, pady=6,
            cursor="hand2",
            command=lambda: self._export("txt"),
        )
        btn_txt.pack(side="left", padx=(0, Spacing.SM))
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=teal_hover))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=teal))

        if self.on_back:
            btn_back = tk.Button(
                parent,
                text="× Volver",
                font=("Segoe UI", 10, "bold"),
                bg="#dc2626", fg="white",
                relief="flat", padx=10, pady=6,
                cursor="hand2",
                command=self._on_back,
            )
            btn_back.pack(side="left")
            btn_back.bind("<Enter>", lambda e: btn_back.config(bg="#b91c1c"))
            btn_back.bind("<Leave>", lambda e: btn_back.config(bg="#dc2626"))

    def _build_table(self, parent):
        """Construye el Treeview con scrollbar vertical."""
        bg = self._bg
        columns = ("fecha", "tipo", "descripcion", "referencia", "monto", "direccion")

        self._tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # Encabezados y anchos de columna
        col_config = [
            ("fecha",       "Fecha",       100),
            ("tipo",        "Tipo",         80),
            ("descripcion", "Descripción", 220),
            ("referencia",  "Referencia",  160),
            ("monto",       "Monto",       110),
            ("direccion",   "Dirección",    90),
        ]
        for col_id, heading, width in col_config:
            self._tree.heading(col_id, text=heading)
            self._tree.column(col_id, width=width, minwidth=60, anchor="w")

        # Tags de color por tipo
        self._tree.tag_configure("ingreso",        background=ROW_COLORS["ingreso"])
        self._tree.tag_configure("egreso",         background=ROW_COLORS["egreso"])
        self._tree.tag_configure("ajuste",         background=ROW_COLORS["ajuste"])
        self._tree.tag_configure("ajuste_entrada", background=ROW_COLORS["ajuste_entrada"])
        self._tree.tag_configure("ajuste_salida",  background=ROW_COLORS["ajuste_salida"])

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_footer(self, parent):
        """Construye el footer con labels de totales apilados verticalmente a la izquierda."""
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]

        self._lbl_ingresos = tk.Label(
            parent,
            text="Total ingresos: $0",
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg=theme["text_primary"],
        )
        self._lbl_ingresos.pack(anchor="w")

        self._lbl_egresos = tk.Label(
            parent,
            text="Total egresos: $0",
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg=theme["text_primary"],
        )
        self._lbl_egresos.pack(anchor="w")

        self._lbl_balance = tk.Label(
            parent,
            text="Balance neto: $0",
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg="#166534",
        )
        self._lbl_balance.pack(anchor="w")

    # ------------------------------------------------------------------
    # Helpers de fecha
    # ------------------------------------------------------------------

    def _get_date_range(self):
        """
        Retorna (date_from, date_to) en formato YYYY-MM-DD
        según el mes y año seleccionados en los comboboxes.
        Si el mes es "Todos" retorna el año completo.
        """
        mes_nombre = self._mes_var.get()
        anio = int(self._anio_var.get())
        if mes_nombre == "Todos":
            return f"{anio:04d}-01-01", f"{anio:04d}-12-31"
        mes_num = MESES.index(mes_nombre) + 1
        ultimo_dia = monthrange(anio, mes_num)[1]
        date_from = f"{anio:04d}-{mes_num:02d}-01"
        date_to   = f"{anio:04d}-{mes_num:02d}-{ultimo_dia:02d}"
        return date_from, date_to

    def _get_period_label(self):
        """Retorna etiqueta de período para el nombre del archivo exportado."""
        mes_nombre = self._mes_var.get()
        anio = self._anio_var.get()
        if mes_nombre == "Todos":
            return f"{anio}"
        mes_num = MESES.index(mes_nombre) + 1
        return f"{anio}-{mes_num:02d}"

    # ------------------------------------------------------------------
    # Carga y actualización
    # ------------------------------------------------------------------

    def _load_movements(self):
        """
        Llama al presenter con los filtros actuales,
        actualiza la tabla y el footer.
        """
        try:
            date_from, date_to = self._get_date_range()

            tipo_sel = self._tipo_var.get()
            movement_type = None
            if tipo_sel != "Todos":
                movement_type = tipo_sel.lower()

            self._movements = self.presenter.consolidate_movements(
                date_from=date_from,
                date_to=date_to,
                movement_type=movement_type,
            )

            totals = self.presenter.calculate_totals(self._movements)
            self._update_table(self._movements)
            self._update_footer(totals)

        except Exception as exc:
            logger.exception("Error al cargar movimientos en LedgerView: %s", exc)
            messagebox.showerror("Error", f"No se pudieron cargar los movimientos:\n{exc}")

    def _update_table(self, movements):
        """Limpia y repuebla el Treeview con la lista de movimientos."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        if not movements:
            self._tree.insert(
                "", "end",
                values=("", "", "No hay movimientos para el período seleccionado.", "", "", ""),
            )
            return

        for mov in movements:
            tipo = mov.get("tipo", "ajuste")
            direccion = mov.get("direccion", "")
            fuente = mov.get("fuente", "")
            monto_fmt = f"${mov.get('monto', 0):,.2f}"

            # Para ajustes de apertura: mostrar "Ingreso" / "Egreso" directamente
            # Para ajustes manuales: mostrar "Ajuste ↑" / "Ajuste ↓"
            if tipo == "ajuste":
                if fuente == "apertura":
                    if direccion == "entrada":
                        tipo_display = "Ingreso"
                        tag = "ajuste_entrada"
                    elif direccion == "salida":
                        tipo_display = "Egreso"
                        tag = "ajuste_salida"
                    else:
                        tipo_display = "Ajuste"
                        tag = "ajuste"
                else:
                    if direccion == "entrada":
                        tipo_display = "Ajuste ↑"
                        tag = "ajuste_entrada"
                    elif direccion == "salida":
                        tipo_display = "Ajuste ↓"
                        tag = "ajuste_salida"
                    else:
                        tipo_display = "Ajuste"
                        tag = "ajuste"
            else:
                tipo_display = tipo.capitalize()
                tag = tipo

            self._tree.insert(
                "", "end",
                values=(
                    mov.get("fecha_display", mov.get("fecha", "")),
                    tipo_display,
                    mov.get("descripcion", ""),
                    mov.get("referencia", ""),
                    monto_fmt,
                    direccion.capitalize(),
                ),
                tags=(tag,),
            )

    def _update_footer(self, totals):
        """Actualiza los labels del footer con los totales calculados."""
        ingresos = totals.get("total_ingresos", 0)
        egresos  = totals.get("total_egresos", 0)
        balance  = totals.get("balance_neto", 0)

        self._lbl_ingresos.config(text=f"Total ingresos: ${ingresos:,.2f}")
        self._lbl_egresos.config(text=f"Total egresos: ${egresos:,.2f}")
        self._lbl_balance.config(
            text=f"Balance neto: ${balance:,.2f}",
            fg="#166534" if balance >= 0 else "#991b1b",
        )

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _clear_filters(self):
        """Resetea los comboboxes al mes/año actual y recarga los movimientos."""
        now = datetime.now()
        self._mes_var.set(MESES[now.month - 1])
        self._anio_var.set(str(now.year))
        self._tipo_var.set("Todos")
        self._load_movements()

    def _export(self, fmt: str):
        """
        Exporta los movimientos actuales al formato indicado (csv o txt).
        Muestra un messagebox con la ruta del archivo generado.
        """
        if not self._movements:
            messagebox.showinfo("Sin datos", "No hay movimientos para exportar.")
            return
        try:
            period_label = self._get_period_label()
            path = self.presenter.export_ledger(self._movements, fmt, period_label)
            messagebox.showinfo(
                "Exportación exitosa",
                f"Archivo generado correctamente:\n{path}",
            )
        except Exception as exc:
            logger.exception("Error al exportar libro de movimientos: %s", exc)
            messagebox.showerror("Error al exportar", f"No se pudo exportar el archivo:\n{exc}")

    def _on_back(self):
        """Navega de vuelta al hub de contabilidad."""
        if self.on_back:
            self.on_back()
