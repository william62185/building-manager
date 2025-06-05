import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date, timedelta
import csv
import calendar

from ...models.payment import Payment
from ...services.payment_service import PaymentService
from ...services.tenant_service import TenantService
from ..components import DataTable, MetricsCard


class PaymentsHistoryView(ttk.Frame):
    """Vista de historial completo de pagos con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        self.all_payments: List[Payment] = []
        self.filtered_payments: List[Payment] = []
        self.current_payment: Optional[Payment] = None
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz del historial de pagos."""
        self.configure(padding="12")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="📊 Historial de Pagos",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Historial completo y análisis de pagos",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        subtitle.pack()
        
        # Botones de navegación
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        back_btn = ttk.Button(
            nav_frame,
            text="← Dashboard Pagos",
            command=self._go_back_to_payments_dashboard,
            bootstyle="outline-secondary"
        )
        back_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # RESUMEN HISTÓRICO (4 cards horizontales)
        metrics_section = ttk.LabelFrame(self, text="📈 Resumen Histórico", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 12))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas históricas
        self.total_payments = MetricsCard(
            all_metrics,
            title="Total de Pagos",
            value="0",
            subtitle="Todos los registros",
            icon="📋",
            color="primary"
        )
        self.total_payments.pack(side=tk.LEFT, expand=True, padx=2)

        self.total_collected = MetricsCard(
            all_metrics,
            title="Total Recaudado",
            value="$0.00",
            subtitle="Monto histórico total",
            icon="💰",
            color="success"
        )
        self.total_collected.pack(side=tk.LEFT, expand=True, padx=2)

        self.monthly_average = MetricsCard(
            all_metrics,
            title="Promedio Mensual",
            value="$0.00",
            subtitle="Recaudación promedio",
            icon="📊",
            color="info"
        )
        self.monthly_average.pack(side=tk.LEFT, expand=True, padx=2)

        self.payment_rate = MetricsCard(
            all_metrics,
            title="Tasa de Cobro",
            value="0%",
            subtitle="Pagos a tiempo",
            icon="🎯",
            color="warning"
        )
        self.payment_rate.pack(side=tk.LEFT, expand=True, padx=2)

        # FILTROS AVANZADOS
        filters_frame = ttk.LabelFrame(self, text="🔧 Filtros de Historial", padding="12")
        filters_frame.pack(fill=tk.X, pady=(0, 12))

        # Primera fila: período y estado
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_row1, text="Período:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.period_filter = tk.StringVar(value="Último año")
        period_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.period_filter,
            values=[
                "Último mes",
                "Últimos 3 meses", 
                "Últimos 6 meses",
                "Último año",
                "Todo el historial",
                "Personalizado"
            ],
            state="readonly",
            width=15
        )
        period_combo.pack(side=tk.LEFT, padx=(0, 15))
        period_combo.bind("<<ComboboxSelected>>", self._on_period_change)

        ttk.Label(filter_row1, text="Estado:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.status_filter,
            values=["Todos", "Completado", "Pendiente", "Cancelado"],
            state="readonly",
            width=12
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(filter_row1, text="Tipo:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.type_filter = tk.StringVar(value="Todos")
        type_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.type_filter,
            values=["Todos", "Renta", "Servicios", "Mantenimiento", "Otros"],
            state="readonly",
            width=12
        )
        type_combo.pack(side=tk.LEFT)
        type_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Segunda fila: fechas personalizadas (inicialmente oculta)
        self.custom_dates_frame = ttk.Frame(filters_frame)
        
        ttk.Label(self.custom_dates_frame, text="Desde:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_date = tk.StringVar()
        start_entry = ttk.Entry(self.custom_dates_frame, textvariable=self.start_date, width=12)
        start_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(self.custom_dates_frame, text="Hasta:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.end_date = tk.StringVar()
        end_entry = ttk.Entry(self.custom_dates_frame, textvariable=self.end_date, width=12)
        end_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(self.custom_dates_frame, text="(DD/MM/YYYY)", 
                 bootstyle="secondary").pack(side=tk.LEFT, padx=(0, 15))

        apply_btn = ttk.Button(
            self.custom_dates_frame,
            text="Aplicar",
            command=self._apply_custom_dates,
            bootstyle="primary"
        )
        apply_btn.pack(side=tk.LEFT)

        # Tercera fila: búsqueda y ordenamiento
        filter_row3 = ttk.Frame(filters_frame)
        filter_row3.pack(fill=tk.X)

        ttk.Label(filter_row3, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        search_entry = ttk.Entry(
            filter_row3,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(filter_row3, text="Ordenar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="Fecha (Reciente)")
        sort_combo = ttk.Combobox(
            filter_row3,
            textvariable=self.sort_var,
            values=[
                "Fecha (Reciente)",
                "Fecha (Antiguo)",
                "Monto (Mayor)",
                "Monto (Menor)",
                "Inquilino A-Z",
                "Tipo de Pago"
            ],
            state="readonly",
            width=15
        )
        sort_combo.pack(side=tk.LEFT, padx=(0, 15))
        sort_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        clear_btn = ttk.Button(
            filter_row3,
            text="🗑️ Limpiar",
            command=self._clear_filters,
            bootstyle="outline-secondary"
        )
        clear_btn.pack(side=tk.LEFT)

        # BARRA DE HERRAMIENTAS
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, pady=(0, 12))

        # Botones de análisis
        analysis_frame = ttk.Frame(toolbar_frame)
        analysis_frame.pack(side=tk.LEFT)

        monthly_report_btn = ttk.Button(
            analysis_frame,
            text="📊 Reporte Mensual",
            command=self._generate_monthly_report,
            bootstyle="info"
        )
        monthly_report_btn.pack(side=tk.LEFT, padx=(0, 8))

        trends_btn = ttk.Button(
            analysis_frame,
            text="📈 Análisis de Tendencias",
            command=self._show_trends,
            bootstyle="success"
        )
        trends_btn.pack(side=tk.LEFT, padx=(0, 8))

        export_btn = ttk.Button(
            analysis_frame,
            text="📤 Exportar Historial",
            command=self._export_history,
            bootstyle="primary"
        )
        export_btn.pack(side=tk.LEFT)

        # Botón de actualizar
        refresh_btn = ttk.Button(
            toolbar_frame,
            text="🔄 Actualizar",
            command=self._refresh_data,
            bootstyle="outline-primary"
        )
        refresh_btn.pack(side=tk.RIGHT)

        # TABLA DE HISTORIAL
        table_frame = ttk.LabelFrame(self, text="📋 Historial de Pagos", padding="8")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Información del período y contador
        info_frame = ttk.Frame(table_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))

        self.period_label = ttk.Label(info_frame, text="Período: Último año")
        self.period_label.pack(side=tk.LEFT)

        self.records_label = ttk.Label(info_frame, text="0 pagos encontrados")
        self.records_label.pack(side=tk.RIGHT)

        # Tabla de historial
        self.table = DataTable(
            table_frame,
            columns=[
                ("date", "Fecha"),
                ("tenant_name", "Inquilino"),
                ("amount", "Monto"),
                ("payment_type", "Tipo"),
                ("status", "Estado"),
                ("days_to_pay", "Días para Pagar"),
                ("description", "Descripción")
            ],
            on_select=self._on_select_payment,
            on_double_click=lambda data: self._show_payment_details(data)
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _load_data(self):
        """Carga todo el historial de pagos."""
        try:
            self.all_payments = self.payment_service.get_all()
            self._apply_filters()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial: {e}")

    def _on_period_change(self, event=None):
        """Maneja cambios en el período."""
        if self.period_filter.get() == "Personalizado":
            self.custom_dates_frame.pack(fill=tk.X, pady=(8, 0))
        else:
            self.custom_dates_frame.pack_forget()
            self._apply_filters()

    def _apply_custom_dates(self):
        """Aplica filtros de fechas personalizadas."""
        self._apply_filters()

    def _on_filter_change(self, event=None):
        """Maneja cambios en los filtros."""
        self._apply_filters()

    def _on_search_change(self, *args):
        """Maneja cambios en la búsqueda."""
        self._apply_filters()

    def _apply_filters(self):
        """Aplica todos los filtros seleccionados."""
        try:
            filtered = list(self.all_payments)
            
            # Filtro por período
            period = self.period_filter.get()
            today = date.today()
            
            if period == "Último mes":
                start_date = today.replace(day=1)
                filtered = [p for p in filtered if p.date >= start_date]
                period_text = f"Último mes ({start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')})"
            elif period == "Últimos 3 meses":
                start_date = today - timedelta(days=90)
                filtered = [p for p in filtered if p.date >= start_date]
                period_text = f"Últimos 3 meses ({start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')})"
            elif period == "Últimos 6 meses":
                start_date = today - timedelta(days=180)
                filtered = [p for p in filtered if p.date >= start_date]
                period_text = f"Últimos 6 meses ({start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')})"
            elif period == "Último año":
                start_date = today - timedelta(days=365)
                filtered = [p for p in filtered if p.date >= start_date]
                period_text = f"Último año ({start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')})"
            elif period == "Personalizado":
                start_str = self.start_date.get().strip()
                end_str = self.end_date.get().strip()
                period_text = "Personalizado"
                
                if start_str:
                    try:
                        start_date = datetime.strptime(start_str, "%d/%m/%Y").date()
                        filtered = [p for p in filtered if p.date >= start_date]
                        period_text += f" desde {start_str}"
                    except ValueError:
                        pass
                
                if end_str:
                    try:
                        end_date = datetime.strptime(end_str, "%d/%m/%Y").date()
                        filtered = [p for p in filtered if p.date <= end_date]
                        period_text += f" hasta {end_str}"
                    except ValueError:
                        pass
            else:  # Todo el historial
                period_text = "Todo el historial"

            # Filtro por estado
            status = self.status_filter.get()
            if status != "Todos":
                filtered = [p for p in filtered if p.status == status]

            # Filtro por tipo
            payment_type = self.type_filter.get()
            if payment_type != "Todos":
                filtered = [p for p in filtered if p.payment_type == payment_type]

            # Filtro por búsqueda
            search_text = self.search_var.get().lower().strip()
            if search_text:
                search_filtered = []
                for payment in filtered:
                    # Buscar en descripción, monto, tipo
                    if (search_text in (payment.description or "").lower() or
                        search_text in str(payment.amount) or
                        search_text in payment.payment_type.lower()):
                        search_filtered.append(payment)
                    else:
                        # Buscar en nombre del inquilino
                        tenant_name = self._get_tenant_name(payment.tenant_id)
                        if search_text in tenant_name.lower():
                            search_filtered.append(payment)
                filtered = search_filtered

            # Aplicar ordenamiento
            sort_by = self.sort_var.get()
            if sort_by == "Fecha (Reciente)":
                filtered.sort(key=lambda p: p.date, reverse=True)
            elif sort_by == "Fecha (Antiguo)":
                filtered.sort(key=lambda p: p.date)
            elif sort_by == "Monto (Mayor)":
                filtered.sort(key=lambda p: p.amount, reverse=True)
            elif sort_by == "Monto (Menor)":
                filtered.sort(key=lambda p: p.amount)
            elif sort_by == "Inquilino A-Z":
                filtered.sort(key=lambda p: self._get_tenant_name(p.tenant_id))
            elif sort_by == "Tipo de Pago":
                filtered.sort(key=lambda p: p.payment_type)

            self.filtered_payments = filtered
            self.period_label.configure(text=f"Período: {period_text}")
            self._update_table()
            
        except Exception as e:
            print(f"Error al aplicar filtros: {e}")
            messagebox.showerror("Error", f"Error al filtrar historial: {e}")

    def _update_table(self):
        """Actualiza la tabla con los pagos filtrados."""
        data = []
        total_amount = Decimal("0")
        completed_count = 0
        on_time_count = 0
        
        for payment in self.filtered_payments:
            # Obtener nombre del inquilino
            tenant_name = self._get_tenant_name(payment.tenant_id)
            
            # Calcular días para pagar
            days_to_pay = self._calculate_days_to_pay(payment)
            
            data.append({
                "id": payment.id,
                "date": payment.date.strftime("%d/%m/%Y"),
                "tenant_name": tenant_name,
                "amount": f"${payment.amount:,.2f}",
                "payment_type": payment.payment_type,
                "status": payment.status,
                "days_to_pay": days_to_pay,
                "description": payment.description or ""
            })
            
            # Calcular estadísticas
            total_amount += payment.amount
            if payment.status == "Completado":
                completed_count += 1
                # Considerar "a tiempo" si se pagó antes o en la fecha límite
                if payment.due_date and payment.date <= payment.due_date:
                    on_time_count += 1

        self.table.set_data(data)
        self.records_label.configure(text=f"{len(data)} pago(s) encontrado(s)")
        
        # Calcular métricas
        if self.filtered_payments:
            # Calcular promedio mensual
            if len(self.filtered_payments) > 0:
                first_date = min(p.date for p in self.filtered_payments)
                last_date = max(p.date for p in self.filtered_payments)
                months_diff = max(1, (last_date.year - first_date.year) * 12 + last_date.month - first_date.month + 1)
                monthly_avg = total_amount / months_diff
            else:
                monthly_avg = Decimal("0")
            
            # Calcular tasa de cobro
            payment_rate = (on_time_count / completed_count * 100) if completed_count > 0 else 0
        else:
            monthly_avg = Decimal("0")
            payment_rate = 0
        
        # Actualizar métricas
        self.total_payments.update_value(str(len(self.filtered_payments)))
        self.total_collected.update_value(f"${total_amount:,.2f}")
        self.monthly_average.update_value(f"${monthly_avg:,.2f}")
        self.payment_rate.update_value(f"{payment_rate:.1f}%")

    def _get_tenant_name(self, tenant_id):
        """Obtiene el nombre del inquilino."""
        try:
            tenant = self.tenant_service.get_by_id(tenant_id)
            return tenant.name if tenant else "Desconocido"
        except:
            return "Desconocido"

    def _calculate_days_to_pay(self, payment):
        """Calcula los días que tardó en pagarse."""
        if not payment.due_date:
            return "Sin fecha límite"
        
        days_diff = (payment.date - payment.due_date).days
        if days_diff <= 0:
            return f"A tiempo ({abs(days_diff)} días antes)" if days_diff < 0 else "A tiempo"
        else:
            return f"{days_diff} días tarde"

    def _clear_filters(self):
        """Limpia todos los filtros."""
        self.period_filter.set("Último año")
        self.status_filter.set("Todos")
        self.type_filter.set("Todos")
        self.sort_var.set("Fecha (Reciente)")
        self.search_var.set("")
        self.start_date.set("")
        self.end_date.set("")
        self.custom_dates_frame.pack_forget()
        self._apply_filters()

    def _on_select_payment(self, data: Dict[str, Any]):
        """Maneja la selección de un pago."""
        if data and "id" in data:
            self.current_payment = self.payment_service.get_by_id(int(data["id"]))
        else:
            self.current_payment = None

    def _show_payment_details(self, data: Dict[str, Any]):
        """Muestra los detalles completos del pago."""
        if data and "id" in data:
            payment = self.payment_service.get_by_id(int(data["id"]))
            if payment:
                tenant = self.tenant_service.get_by_id(payment.tenant_id)
                tenant_name = tenant.name if tenant else "Desconocido"
                days_to_pay = self._calculate_days_to_pay(payment)
                
                details = f"""
DETALLES DEL PAGO HISTÓRICO

Inquilino: {tenant_name}
Fecha de Pago: {payment.date.strftime('%d/%m/%Y')}
Monto: ${payment.amount:,.2f}
Tipo de Pago: {payment.payment_type}
Estado: {payment.status}
Fecha Límite: {payment.due_date.strftime('%d/%m/%Y') if payment.due_date else 'No especificada'}
Tiempo de Pago: {days_to_pay}
Descripción: {payment.description or 'Sin descripción'}
"""
                messagebox.showinfo("Detalles del Pago", details)

    def _generate_monthly_report(self):
        """Genera un reporte mensual."""
        messagebox.showinfo(
            "Reporte Mensual",
            "Generando reporte mensual de pagos...\n\n" +
            "En versiones futuras se generará un PDF con:\n" +
            "• Resumen de ingresos por mes\n" +
            "• Comparativa con períodos anteriores\n" +
            "• Análisis de inquilinos morosos\n" +
            "• Gráficos de tendencias"
        )

    def _show_trends(self):
        """Muestra análisis de tendencias."""
        messagebox.showinfo(
            "Análisis de Tendencias",
            "Mostrando análisis de tendencias...\n\n" +
            "En versiones futuras se mostrará:\n" +
            "• Gráfico de ingresos mensuales\n" +
            "• Tendencias de pagos por inquilino\n" +
            "• Patrones de pago estacionales\n" +
            "• Predicciones de flujo de caja"
        )

    def _export_history(self):
        """Exporta el historial a CSV."""
        if not self.filtered_payments:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Exportar historial de pagos"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = [
                        "Fecha", "Inquilino", "Monto", "Tipo", "Estado", 
                        "Fecha Límite", "Días para Pagar", "Descripción"
                    ]
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for payment in self.filtered_payments:
                        tenant_name = self._get_tenant_name(payment.tenant_id)
                        days_to_pay = self._calculate_days_to_pay(payment)
                        
                        row = [
                            payment.date.strftime("%d/%m/%Y"),
                            tenant_name,
                            f"${payment.amount:,.2f}",
                            payment.payment_type,
                            payment.status,
                            payment.due_date.strftime("%d/%m/%Y") if payment.due_date else "",
                            days_to_pay,
                            payment.description or ""
                        ]
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Historial exportado correctamente a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar historial: {e}")

    def _refresh_data(self):
        """Actualiza los datos del historial."""
        self._load_data()

    def _go_back_to_payments_dashboard(self):
        """Vuelve al dashboard de pagos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_dashboard')

    def refresh(self):
        """Actualiza la vista."""
        self._refresh_data() 