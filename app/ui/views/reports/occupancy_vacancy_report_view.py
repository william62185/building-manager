"""
Vista de reporte de Ocupación y Vacancia
Muestra la tasa de ocupación y tiempo de vacancia por apartamento
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Any
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import tenant_service

class OccupancyVacancyReportView(tk.Frame):
    """Vista de reporte de ocupación y vacancia. Acepta module_context para colores: 'reportes' (naranja) o 'administración' (morado)."""
    
    def __init__(self, parent, on_back: Callable, on_navigate: Callable = None, module_context: str = "administración"):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate = on_navigate
        self._module_context = module_context if module_context in ("reportes", "administración") else "administración"
        self._create_layout()
        self._load_data()
    
    def _create_layout(self):
        """Crea el layout principal del reporte"""
        cb = self._content_bg
        colors = get_module_colors(self._module_context)

        # Métricas
        metrics_frame = tk.Frame(self, bg=cb)
        metrics_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, Spacing.MD))
        self.metrics_container = tk.Frame(metrics_frame, bg=cb)
        self.metrics_container.pack(fill="x", expand=True)

        # Área de tabla con toolbar integrado
        table_area = tk.Frame(self, bg=cb)
        table_area.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))

        # Contenedor de la tabla (primero, para que ocupe el espacio principal)
        self.content_frame = tk.Frame(table_area, bg=cb)
        self.content_frame.pack(fill="both", expand=True)

        # Toolbar pegado debajo de la tabla
        toolbar = tk.Frame(table_area, bg=cb)
        toolbar.pack(fill="x", pady=(4, 0))
        from manager.app.ui.components.modern_widgets import create_rounded_button
        btn_export = create_rounded_button(
            toolbar,
            text="📄 Exportar",
            bg_color=colors["primary"],
            fg_color="white",
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._show_export_dialog,
            padx=14,
            pady=6,
            radius=4,
            border_color=colors["primary"],
        )
        btn_export.pack(side="right")

        # Reservados
        self.chart_frame = tk.Frame(self, bg=cb)
        self.table_header_frame = tk.Frame(self, bg=cb)
    
    def _load_data(self):
        """Carga y procesa los datos de ocupación"""
        apartments = apartment_service.get_all_apartments()
        tenants = tenant_service.get_all_tenants()
        
        # Filtrar solo inquilinos activos (excluir inactivos)
        active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
        
        # Crear mapa de apartamento -> inquilino (solo activos)
        apt_to_tenant = {}
        for tenant in active_tenants:
            apt_id = tenant.get("apartamento")
            if apt_id:
                apt_to_tenant[str(apt_id)] = tenant
        
        # Calcular estadísticas
        total_apartments = len(apartments)
        occupied = 0
        available = 0
        maintenance = 0
        
        self.apartment_data = []
        
        for apt in apartments:
            apt_id = str(apt.get("id"))
            status = apt.get("status", "Disponible")
            tenant = apt_to_tenant.get(apt_id)
            
            if status == "Ocupado":
                occupied += 1
            elif status == "Disponible":
                available += 1
            elif status == "En Mantenimiento":
                maintenance += 1
            
            # Calcular días de vacancia si está disponible
            vacancy_days = None
            if status == "Disponible" and tenant:
                # Si hay un inquilino pero el apartamento está disponible, 
                # podría ser que el inquilino se fue recientemente
                fecha_ingreso = tenant.get("fecha_ingreso", "")
                if fecha_ingreso:
                    try:
                        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%d/%m/%Y")
                        vacancy_days = (datetime.now() - fecha_ingreso_dt).days
                    except:
                        pass
            
            unit_type = apt.get('unit_type', 'Apartamento Estándar')
            unit_number = apt.get('number', 'N/A')
            
            if unit_type == "Local Comercial":
                title_text = f"Local: {unit_number}"
            elif unit_type == "Penthouse":
                title_text = f"Penthouse: {unit_number}"
            elif unit_type == "Depósito":
                title_text = f"Depósito: {unit_number}"
            elif unit_type == "Apartamento Estándar":
                title_text = f"Apto: {unit_number}"
            else:
                title_text = f"{unit_type}: {unit_number}"
            
            self.apartment_data.append({
                "id": apt.get("id"),
                "title": title_text,
                "status": status,
                "tenant": tenant.get("nombre") if tenant else None,
                "rent": tenant.get("valor_arriendo") if tenant else apt.get("base_rent", 0),
                "vacancy_days": vacancy_days,
                "floor": apt.get("floor", ""),
                "unit_type": unit_type
            })
        
        # Mostrar métricas
        self._show_metrics(total_apartments, occupied, available, maintenance)
        
        # Mostrar detalles
        self._show_details()
    
    def _show_metrics(self, total: int, occupied: int, available: int, maintenance: int):
        """Muestra las métricas generales y la gráfica de torta del estado de vacancia."""
        self._total = total
        self._occupied = occupied
        self._available = available
        self._maintenance = maintenance

        # Gráfica de torta (pie chart) a la derecha de la tabla
        cb = getattr(self, "_content_bg", "#f5f5f5")
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        chart_size = 180
        pie_canvas = tk.Canvas(
            self.chart_frame,
            width=chart_size,
            height=chart_size,
            highlightthickness=0,
            bg=cb,
        )
        pie_canvas.pack()
        cx, cy = chart_size // 2, chart_size // 2
        r = min(cx, cy) - 10
        if total > 0:
            # Colores: Ocupadas verde, Disponibles naranja, Mantenimiento azul
            segments = [
                (occupied, "#10b981"),
                (available, "#f59e0b"),
                (maintenance, "#6366f1"),
            ]
            start = 0
            for count, color in segments:
                if count <= 0:
                    continue
                extent = 360 * (count / total)
                pie_canvas.create_arc(
                    cx - r, cy - r, cx + r, cy + r,
                    start=start, extent=extent,
                    fill=color, outline="#333", width=1,
                    style="pieslice",
                )
                start += extent
        else:
            pie_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#e5e7eb", outline="#9ca3af")
            pie_canvas.create_text(cx, cy, text="Sin datos", font=("Segoe UI", 10), fill="#6b7280")
        tk.Label(
            self.chart_frame,
            text="Estado de vacancia",
            font=("Segoe UI", 9, "bold"),
            fg="#374151",
            bg=cb,
        ).pack(pady=(4, 0))

        for widget in self.metrics_container.winfo_children():
            widget.destroy()
        
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        vacancy_rate = (available / total * 100) if total > 0 else 0
        
        metrics = [
            ("Total Unidades", str(total), "#3b82f6"),
            ("Ocupadas", f"{occupied} ({occupancy_rate:.1f}%)", "#10b981"),
            ("Disponibles", f"{available} ({vacancy_rate:.1f}%)", "#f59e0b"),
            ("Mantenimiento", str(maintenance), "#6366f1")
        ]
        
        cb = getattr(self, "_content_bg", "#f5f5f5")
        # Cards de métricas: naranja claro si se abrió desde Reportes, morado claro si desde Administración
        if self._module_context == "reportes":
            card_bg = get_module_colors("reportes")["light"]  # #fed7aa
        else:
            card_bg = "#f3e8ff"
        for i, (label, value, color) in enumerate(metrics):
            metric_frame = tk.Frame(self.metrics_container, bg=card_bg, relief="flat", bd=0)
            metric_frame.pack(side="left", fill="both", expand=True, padx=Spacing.SM)
            
            tk.Label(
                metric_frame,
                text=label,
                font=("Segoe UI", 10),
                fg="#666",
                bg=card_bg,
            ).pack(pady=(Spacing.MD, Spacing.XS))
            
            tk.Label(
                metric_frame,
                text=value,
                font=("Segoe UI", 16, "bold"),
                fg=color,
                bg=card_bg,
            ).pack(pady=(0, Spacing.MD))
    
    def _show_details(self):
        """Muestra los detalles por apartamento en un Treeview."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.table_header_frame.winfo_children():
            widget.destroy()

        cb = getattr(self, "_content_bg", "#f5f5f5")

        if not self.apartment_data:
            tk.Label(
                self.content_frame,
                text="No hay apartamentos registrados.",
                font=("Segoe UI", 12),
                fg="#666",
                bg=cb,
            ).pack(pady=Spacing.XL)
            return

        # Colores según contexto
        if self._module_context == "reportes":
            header_bg = get_module_colors("reportes")["hover"]
        else:
            header_bg = "#7c3aed"

        # Estilo del Treeview con cuadrículas
        style = ttk.Style()
        style.theme_use("clam")
        tv_style = "OccReport.Treeview"
        style.configure(tv_style,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#1f2937",
            rowheight=30,
            font=("Segoe UI", 9),
            relief="flat",
            borderwidth=0,
            # líneas entre filas simuladas con rowheight + separador
        )
        style.configure(f"{tv_style}.Heading",
            background=header_bg,
            foreground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(4, 7),
            borderwidth=0,
        )
        style.map(tv_style, background=[("selected", "#c4b5fd")])
        style.map(f"{tv_style}.Heading", background=[("active", header_bg)])
        # Separador entre filas: usar layout con línea inferior
        style.layout(tv_style, [
            ("Treeview.treearea", {"sticky": "nswe"}),
        ])

        # Frame exterior con borde y fondo de cuadrícula (simula líneas entre columnas)
        tree_border = tk.Frame(self.content_frame, bg="#d1d5db", bd=1, relief="solid")
        tree_border.pack(fill="both", expand=True)

        columns = ("unidad", "estado", "inquilino", "arriendo", "piso", "tipo")
        tree = ttk.Treeview(
            tree_border,
            columns=columns,
            show="headings",
            style=tv_style,
            selectmode="browse",
        )

        col_config = [
            ("unidad",    "Unidad",    150, "center"),
            ("estado",    "Estado",    110, "center"),
            ("inquilino", "Inquilino", 170, "center"),
            ("arriendo",  "Arriendo",  110, "center"),
            ("piso",      "Piso",       60, "center"),
            ("tipo",      "Tipo",      160, "center"),
        ]
        for col_id, heading, width, anchor in col_config:
            tree.heading(col_id, text=heading, anchor="center")
            tree.column(col_id, width=width, minwidth=width, anchor=anchor, stretch=True)

        # Tags por estado con fondo de color + separador de fila (borde inferior simulado)
        tree.tag_configure("ocupado",       background="#d1fae5", foreground="#065f46")
        tree.tag_configure("disponible",    background="#fef3c7", foreground="#92400e")
        tree.tag_configure("mantenimiento", background="#ede9fe", foreground="#4c1d95")
        tree.tag_configure("default",       background="#f9fafb", foreground="#1f2937")
        # Filas alternas para reforzar separación visual
        tree.tag_configure("ocupado_alt",       background="#a7f3d0", foreground="#065f46")
        tree.tag_configure("disponible_alt",    background="#fde68a", foreground="#92400e")
        tree.tag_configure("mantenimiento_alt", background="#ddd6fe", foreground="#4c1d95")
        tree.tag_configure("default_alt",       background="#f3f4f6", foreground="#1f2937")

        sorted_data = sorted(self.apartment_data, key=lambda x: (
            x.get("unit_type") != "Apartamento Estándar",
            int(x.get("floor", 0)) if str(x.get("floor", "0")).isdigit() else 999,
            x.get("title", ""),
        ))

        for idx, apt in enumerate(sorted_data):
            rent = apt.get("rent", 0)
            rent_display = f"${float(rent):,.0f}" if rent else "---"
            status = apt.get("status", "Disponible")
            alt = "_alt" if idx % 2 == 1 else ""
            if status == "Ocupado":
                tag = f"ocupado{alt}"
            elif status == "Disponible":
                tag = f"disponible{alt}"
            elif status == "En Mantenimiento":
                tag = f"mantenimiento{alt}"
            else:
                tag = f"default{alt}"
            tree.insert("", "end", tags=(tag,), values=(
                apt.get("title", ""),
                status,
                apt.get("tenant") or "---",
                rent_display,
                str(apt.get("floor", "")),
                apt.get("unit_type", ""),
            ))

        scrollbar = ttk.Scrollbar(tree_border, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _get_report_preview_text(self) -> str:
        """Genera el texto de vista previa del informe (mismo contenido que el TXT exportado)."""
        total, occupied, available, maintenance, sorted_data = self._get_export_data()
        occ_rate = (occupied / total * 100) if total > 0 else 0
        vac_rate = (available / total * 100) if total > 0 else 0
        lines = [
            "=" * 60,
            "REPORTE DE OCUPACIÓN Y VACANCIA",
            "Building Manager Pro",
            "=" * 60,
            "",
            f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            "RESUMEN",
            "-" * 40,
            f"Total de unidades:     {total}",
            f"Ocupadas:             {occupied} ({occ_rate:.1f}%)",
            f"Disponibles:          {available} ({vac_rate:.1f}%)",
            f"En mantenimiento:     {maintenance}",
            "",
            "DETALLE POR UNIDAD",
            "-" * 40,
            f"{'Unidad':<22} {'Estado':<16} {'Inquilino':<20} {'Arriendo':<12} {'Piso':<6} {'Tipo':<20}",
            "-" * 40,
        ]
        for apt in sorted_data:
            tenant = apt.get("tenant") or "---"
            rent = apt.get("rent", 0)
            rent_str = f"${float(rent):,.0f}" if rent else "---"
            lines.append(
                f"{apt.get('title', ''):<22} {apt.get('status', ''):<16} {tenant[:18]:<20} {rent_str:<12} {str(apt.get('floor', '')):<6} {str(apt.get('unit_type', ''))[:18]:<20}"
            )
        lines.extend(["", "=" * 60])
        return "\n".join(lines)

    def _show_export_dialog(self):
        """Abre la ventana de exportación con vista previa. Colores según module_context (reportes naranja, administración morado)."""
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Exportar reporte - Ocupación y Vacancia")
        win.geometry("720x580")
        win.minsize(600, 480)
        win.transient(self.winfo_toplevel())
        win.grab_set()

        mod_colors = get_module_colors(self._module_context)
        header_bg = mod_colors["primary"]
        header = tk.Frame(win, bg=header_bg, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="Exportar reporte - Ocupación y Vacancia",
            font=("Segoe UI", 13, "bold"),
            bg=header_bg,
            fg="white",
        ).pack(side="left", padx=12, pady=10)
        btn_frame = tk.Frame(header, bg=header_bg)
        btn_frame.pack(side="right", padx=10)

        def do_export(fmt):
            if fmt == "csv":
                self._export_report_csv()
            elif fmt == "txt":
                self._export_report_txt()

        btn_opts = dict(font=("Segoe UI", 9), fg="white", relief="flat", padx=12, pady=5, cursor="hand2")
        export_bg = mod_colors["primary"]
        export_hover = mod_colors.get("hover", "#5b21b6")
        close_bg = "#dc2626"
        close_hover = "#b91c1c"

        btn_csv = tk.Button(
            btn_frame,
            text="Exportar CSV",
            bg=export_bg,
            **btn_opts,
            command=lambda: do_export("csv"),
        )
        btn_csv.pack(side="left", padx=3)
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=export_hover))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=export_bg))

        btn_txt = tk.Button(
            btn_frame,
            text="Exportar TXT",
            bg=export_bg,
            **btn_opts,
            command=lambda: do_export("txt"),
        )
        btn_txt.pack(side="left", padx=3)
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=export_hover))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=export_bg))

        btn_close = tk.Button(
            btn_frame,
            text="× Cerrar",
            bg=close_bg,
            width=8,
            **btn_opts,
            command=win.destroy,
        )
        btn_close.pack(side="left", padx=3)
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=close_hover))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=close_bg))

        body = tk.Frame(win, bg="#ffffff", padx=16, pady=12)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        tk.Label(
            body,
            text="Vista previa del informe. Elige el formato de exportación abajo.",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#374151",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        preview_frame = tk.Frame(body, bg="#f8fafc", relief="solid", bd=1)
        preview_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_inner = tk.Frame(preview_frame, bg="#f8fafc", padx=8, pady=8)
        preview_inner.pack(fill="both", expand=True)
        preview_inner.grid_columnconfigure(0, weight=1)
        preview_inner.grid_rowconfigure(0, weight=1)

        text_preview = tk.Text(
            preview_inner,
            font=("Consolas", 9),
            wrap="none",
            bg="#ffffff",
            fg="#1f2937",
            relief="flat",
            padx=8,
            pady=8,
        )
        scroll_y = ttk.Scrollbar(preview_inner)
        scroll_x = ttk.Scrollbar(preview_inner, orient="horizontal")
        text_preview.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.configure(command=text_preview.yview)
        scroll_x.configure(command=text_preview.xview)
        text_preview.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        preview_inner.grid_columnconfigure(0, weight=1)
        preview_inner.grid_rowconfigure(0, weight=1)

        preview_text = self._get_report_preview_text()
        text_preview.insert("1.0", preview_text)
        text_preview.config(state="disabled")

        def on_mousewheel(event):
            text_preview.yview_scroll(int(-1 * (event.delta / 120)), "units")
        text_preview.bind("<MouseWheel>", on_mousewheel)

    def _show_export_success_dialog(self, filepath: Path):
        from manager.app.ui.components.export_success_dialog import show_export_success_dialog
        mod_colors = get_module_colors(self._module_context)
        show_export_success_dialog(self, filepath, module_color=mod_colors.get("primary", "#2563eb"))

    def _get_export_data(self):
        """Devuelve (total, occupied, available, maintenance) y lista de filas para detalle."""
        total = getattr(self, "_total", 0)
        occupied = getattr(self, "_occupied", 0)
        available = getattr(self, "_available", 0)
        maintenance = getattr(self, "_maintenance", 0)
        sorted_data = sorted(
            getattr(self, "apartment_data", []),
            key=lambda x: (
                x.get("unit_type") != "Apartamento Estándar",
                int(x.get("floor", 0)) if str(x.get("floor", "0")).isdigit() else 999,
                x.get("title", ""),
            ),
        )
        return total, occupied, available, maintenance, sorted_data

    def _export_report_txt(self):
        """Exporta el reporte a TXT y muestra ventana de confirmación."""
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filepath = EXPORTS_DIR / f"reporte_ocupacion_vacancia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo preparar la ruta de exportación: {e}")
            return
        total, occupied, available, maintenance, sorted_data = self._get_export_data()
        occ_rate = (occupied / total * 100) if total > 0 else 0
        vac_rate = (available / total * 100) if total > 0 else 0
        lines = [
            "=" * 60,
            "REPORTE DE OCUPACIÓN Y VACANCIA",
            "Building Manager Pro",
            "=" * 60,
            "",
            f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            "RESUMEN",
            "-" * 40,
            f"Total de unidades:     {total}",
            f"Ocupadas:             {occupied} ({occ_rate:.1f}%)",
            f"Disponibles:          {available} ({vac_rate:.1f}%)",
            f"En mantenimiento:     {maintenance}",
            "",
            "DETALLE POR UNIDAD",
            "-" * 40,
            f"{'Unidad':<22} {'Estado':<16} {'Inquilino':<20} {'Arriendo':<12} {'Piso':<6} {'Tipo':<20}",
            "-" * 40,
        ]
        for apt in sorted_data:
            tenant = apt.get("tenant") or "---"
            rent = apt.get("rent", 0)
            rent_str = f"${float(rent):,.0f}" if rent else "---"
            lines.append(
                f"{apt.get('title', ''):<22} {apt.get('status', ''):<16} {tenant[:18]:<20} {rent_str:<12} {str(apt.get('floor', '')):<6} {str(apt.get('unit_type', ''))[:18]:<20}"
            )
        lines.extend(["", "=" * 60])
        try:
            with open(filepath, "w", encoding="utf-8-sig") as f:
                f.write("\n".join(lines))
            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def _export_report_csv(self):
        """Exporta el reporte a CSV con formato para Excel (BOM UTF-8, columnas bien delimitadas)."""
        import csv
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filepath = EXPORTS_DIR / f"reporte_ocupacion_vacancia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo preparar la ruta de exportación: {e}")
            return
        total, occupied, available, maintenance, sorted_data = self._get_export_data()
        try:
            # utf-8-sig: añade BOM para que Excel detecte UTF-8 y separen bien las columnas
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                w.writerow(["Reporte de Ocupación y Vacancia", "Building Manager Pro"])
                w.writerow([f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
                w.writerow([])
                w.writerow(["RESUMEN"])
                w.writerow(["Concepto", "Valor"])
                w.writerow(["Total de unidades", total])
                occ_pct = (occupied / total * 100) if total else 0
                vac_pct = (available / total * 100) if total else 0
                w.writerow(["Ocupadas", f"{occupied} ({occ_pct:.1f}%)"])
                w.writerow(["Disponibles", f"{available} ({vac_pct:.1f}%)"])
                w.writerow(["En mantenimiento", maintenance])
                w.writerow([])
                w.writerow(["DETALLE POR UNIDAD"])
                w.writerow(["Unidad", "Estado", "Inquilino", "Arriendo", "Piso", "Tipo"])
                for apt in sorted_data:
                    tenant = apt.get("tenant") or "---"
                    rent = apt.get("rent", 0)
                    rent_str = f"{float(rent):,.0f}" if rent else "---"
                    w.writerow([
                        apt.get("title", ""),
                        apt.get("status", ""),
                        tenant,
                        rent_str,
                        str(apt.get("floor", "")),
                        str(apt.get("unit_type", "")),
                    ])
            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def _export_report_excel(self):
        """Exporta el reporte a Excel (.xlsx) y muestra ventana de confirmación."""
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filepath = EXPORTS_DIR / f"reporte_ocupacion_vacancia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo preparar la ruta de exportación: {e}")
            return
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment
        except ImportError:
            messagebox.showerror("Error", "No se encontró el módulo openpyxl. Instálalo con: pip install openpyxl")
            return
        total, occupied, available, maintenance, sorted_data = self._get_export_data()
        occ_rate = (occupied / total * 100) if total > 0 else 0
        vac_rate = (available / total * 100) if total > 0 else 0
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Ocupación y Vacancia"
            ws.append(["REPORTE DE OCUPACIÓN Y VACANCIA", "Building Manager Pro"])
            ws.append([f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
            ws.append([])
            ws.append(["RESUMEN"])
            ws.append(["Total de unidades", total])
            ws.append(["Ocupadas", f"{occupied} ({occ_rate:.1f}%)"])
            ws.append(["Disponibles", f"{available} ({vac_rate:.1f}%)"])
            ws.append(["En mantenimiento", maintenance])
            ws.append([])
            ws.append(["DETALLE POR UNIDAD"])
            ws.append(["Unidad", "Estado", "Inquilino", "Arriendo", "Piso", "Tipo"])
            for apt in sorted_data:
                tenant = apt.get("tenant") or "---"
                rent = apt.get("rent", 0)
                rent_str = f"${float(rent):,.0f}" if rent else "---"
                ws.append([
                    apt.get("title", ""),
                    apt.get("status", ""),
                    tenant,
                    rent_str,
                    str(apt.get("floor", "")),
                    str(apt.get("unit_type", "")),
                ])
            wb.save(filepath)
            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo Excel: {e}")

    def _create_navigation_buttons(self, parent):
        """Crea los botones de navegación. Colores según module_context: reportes (naranja) o administración (morado)."""
        from manager.app.ui.components.icons import Icons
        
        colors = get_module_colors(self._module_context)
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors.get("text", "#1f2937")
        
        def go_to_dashboard():
            if hasattr(self, 'on_navigate') and self.on_navigate is not None:
                try:
                    self.on_navigate("dashboard")
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            try:
                root = self.winfo_toplevel()
                for child in root.winfo_children():
                    if (hasattr(child, '_navigate_to') and 
                        hasattr(child, '_load_view') and 
                        hasattr(child, 'views_container')):
                        try:
                            child._navigate_to("dashboard")
                            return
                        except Exception as e:
                            print(f"Error al navegar desde root: {e}")
            except Exception as e:
                print(f"Error en búsqueda desde root: {e}")
            
            widget = self.master
            max_depth = 15
            depth = 0
            while widget and depth < max_depth:
                if (hasattr(widget, '_navigate_to') and 
                    hasattr(widget, '_load_view') and 
                    hasattr(widget, 'views_container')):
                    try:
                        widget._navigate_to("dashboard")
                        return
                    except Exception as e:
                        print(f"Error al navegar: {e}")
                        break
                widget = getattr(widget, 'master', None)
                depth += 1
            
            if self.on_back:
                self.on_back()
        
        # Orden visual: Exportar -> Dashboard -> Volver (colores según module_context)
        btn_secondary = theme_manager.themes[theme_manager.current_theme].get("btn_secondary_bg", "#e5e7eb")
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=btn_secondary,
            fg_color=purple_primary,
            hover_bg=purple_light,
            hover_fg=purple_text,
            command=self.on_back,
            padx=16,
            pady=8,
            radius=4,
            border_color=purple_light
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))

        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color=purple_hover
        )
        btn_dashboard.pack(side="right", padx=(Spacing.MD, 0))

        btn_export = create_rounded_button(
            parent,
            text="📄 Exportar",
            bg_color=purple_light,
            fg_color=purple_primary,
            hover_bg=purple_hover,
            hover_fg="white",
            command=self._show_export_dialog,
            padx=14,
            pady=8,
            radius=4,
            border_color=purple_primary
        )
        btn_export.pack(side="right")
