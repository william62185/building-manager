import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date
import csv

from ...models.payment import Payment
from ...services.payment_service import PaymentService
from ...services.tenant_service import TenantService
from ..components import DataTable, MetricsCard


class PaymentsSearchView(ttk.Frame):
    """Vista de búsqueda avanzada de pagos con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        self.filtered_payments: List[Payment] = []
        self.current_payment: Optional[Payment] = None
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de búsqueda de pagos."""
        self.configure(padding="12")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="🔍 Búsqueda de Pagos",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Búsqueda avanzada y gestión de pagos",
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

        # RESUMEN RÁPIDO DE RESULTADOS (4 cards horizontales)
        metrics_section = ttk.LabelFrame(self, text="📊 Resumen de Resultados", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 12))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas de resultados
        self.total_found = MetricsCard(
            all_metrics,
            title="Pagos Encontrados",
            value="0",
            subtitle="Total de registros",
            icon="📋",
            color="primary"
        )
        self.total_found.pack(side=tk.LEFT, expand=True, padx=2)

        self.total_amount = MetricsCard(
            all_metrics,
            title="Monto Total",
            value="$0.00",
            subtitle="Suma de pagos",
            icon="💰",
            color="success"
        )
        self.total_amount.pack(side=tk.LEFT, expand=True, padx=2)

        self.completed_payments = MetricsCard(
            all_metrics,
            title="Pagos Completados",
            value="0",
            subtitle="Confirmados",
            icon="✅",
            color="info"
        )
        self.completed_payments.pack(side=tk.LEFT, expand=True, padx=2)

        self.pending_payments = MetricsCard(
            all_metrics,
            title="Pagos Pendientes",
            value="0",
            subtitle="Sin confirmar",
            icon="⏰",
            color="warning"
        )
        self.pending_payments.pack(side=tk.LEFT, expand=True, padx=2)

        # BARRA DE BÚSQUEDA Y FILTROS
        search_frame = ttk.LabelFrame(self, text="🔍 Criterios de Búsqueda", padding="12")
        search_frame.pack(fill=tk.X, pady=(0, 12))

        # Primera fila: búsqueda por texto
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_row1, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        search_entry = ttk.Entry(
            search_row1,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(search_row1, text="(Inquilino, descripción, monto...)", 
                 bootstyle="secondary").pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(
            search_row1,
            text="🗑️ Limpiar",
            command=self._clear_search,
            bootstyle="outline-secondary"
        )
        clear_btn.pack(side=tk.LEFT)

        # Segunda fila: filtros
        search_row2 = ttk.Frame(search_frame)
        search_row2.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_row2, text="Estado:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(
            search_row2,
            textvariable=self.status_filter,
            values=["Todos", "Completado", "Pendiente", "Cancelado"],
            state="readonly",
            width=12
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(search_row2, text="Tipo:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.type_filter = tk.StringVar(value="Todos")
        type_combo = ttk.Combobox(
            search_row2,
            textvariable=self.type_filter,
            values=["Todos", "Renta", "Servicios", "Mantenimiento", "Otros"],
            state="readonly",
            width=12
        )
        type_combo.pack(side=tk.LEFT, padx=(0, 15))
        type_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(search_row2, text="Ordenar por:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="Fecha (Desc)")
        sort_combo = ttk.Combobox(
            search_row2,
            textvariable=self.sort_var,
            values=["Fecha (Desc)", "Fecha (Asc)", "Monto (Desc)", "Monto (Asc)", "Inquilino"],
            state="readonly",
            width=15
        )
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Tercera fila: filtros por fechas
        search_row3 = ttk.Frame(search_frame)
        search_row3.pack(fill=tk.X)

        ttk.Label(search_row3, text="Desde:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_date = tk.StringVar()
        start_entry = ttk.Entry(search_row3, textvariable=self.start_date, width=12)
        start_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(search_row3, text="Hasta:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.end_date = tk.StringVar()
        end_entry = ttk.Entry(search_row3, textvariable=self.end_date, width=12)
        end_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(search_row3, text="(DD/MM/YYYY)", 
                 bootstyle="secondary").pack(side=tk.LEFT, padx=(0, 15))

        search_btn = ttk.Button(
            search_row3,
            text="🔍 Buscar",
            command=self._apply_filters,
            bootstyle="primary"
        )
        search_btn.pack(side=tk.LEFT)

        # BARRA DE HERRAMIENTAS
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, pady=(0, 12))

        # Botones de acción
        actions_left = ttk.Frame(toolbar_frame)
        actions_left.pack(side=tk.LEFT)

        export_btn = ttk.Button(
            actions_left,
            text="📤 Exportar Resultados",
            command=self._export_data,
            bootstyle="success"
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 8))

        refresh_btn = ttk.Button(
            actions_left,
            text="🔄 Actualizar",
            command=self._refresh_data,
            bootstyle="info"
        )
        refresh_btn.pack(side=tk.LEFT)

        # TABLA DE RESULTADOS
        table_frame = ttk.LabelFrame(self, text="📋 Resultados de Búsqueda", padding="8")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Contador de registros
        self.records_label = ttk.Label(table_frame, text="0 pagos encontrados")
        self.records_label.pack(anchor=tk.W, pady=(0, 5))

        # Tabla de pagos
        self.table = DataTable(
            table_frame,
            columns=[
                ("date", "Fecha"),
                ("tenant_name", "Inquilino"),
                ("amount", "Monto"),
                ("payment_type", "Tipo"),
                ("status", "Estado"),
                ("description", "Descripción")
            ],
            on_select=self._on_select_payment,
            on_double_click=lambda data: self._show_payment_details(data)
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _load_data(self):
        """Carga todos los pagos."""
        try:
            payments = self.payment_service.get_all()
            self.filtered_payments = payments
            self._update_table()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pagos: {e}")

    def _update_table(self):
        """Actualiza la tabla con los pagos filtrados."""
        data = []
        total_amount = Decimal("0")
        completed_count = 0
        pending_count = 0
        
        for payment in self.filtered_payments:
            # Obtener nombre del inquilino
            tenant_name = "Desconocido"
            try:
                tenant = self.tenant_service.get_by_id(payment.tenant_id)
                if tenant:
                    tenant_name = tenant.name
            except:
                pass
            
            data.append({
                "id": payment.id,
                "date": payment.date.strftime("%d/%m/%Y") if payment.date else "",
                "tenant_name": tenant_name,
                "amount": f"${payment.amount:,.2f}",
                "payment_type": payment.payment_type,
                "status": payment.status,
                "description": payment.description or ""
            })
            
            # Calcular estadísticas
            total_amount += payment.amount
            if payment.status == "Completado":
                completed_count += 1
            else:
                pending_count += 1
        
        self.table.set_data(data)
        self.records_label.configure(text=f"{len(data)} pago(s) encontrado(s)")
        
        # Actualizar métricas
        self.total_found.update_value(str(len(data)))
        self.total_amount.update_value(f"${total_amount:,.2f}")
        self.completed_payments.update_value(str(completed_count))
        self.pending_payments.update_value(str(pending_count))

    def _on_search_change(self, *args):
        """Maneja cambios en la búsqueda."""
        self._apply_filters()

    def _on_filter_change(self, event=None):
        """Maneja cambios en los filtros."""
        self._apply_filters()

    def _apply_filters(self):
        """Aplica búsqueda y filtros."""
        try:
            search_text = self.search_var.get().lower().strip()
            status_filter = self.status_filter.get()
            type_filter = self.type_filter.get()
            sort_by = self.sort_var.get()
            start_date_str = self.start_date.get().strip()
            end_date_str = self.end_date.get().strip()

            # Obtener todos los pagos
            all_payments = self.payment_service.get_all()
            
            # Aplicar filtro de estado
            if status_filter != "Todos":
                all_payments = [p for p in all_payments if p.status == status_filter]
            
            # Aplicar filtro de tipo
            if type_filter != "Todos":
                all_payments = [p for p in all_payments if p.payment_type == type_filter]
            
            # Aplicar filtro de fechas
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
                    all_payments = [p for p in all_payments if p.date >= start_date]
                except ValueError:
                    pass
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()
                    all_payments = [p for p in all_payments if p.date <= end_date]
                except ValueError:
                    pass
            
            # Aplicar búsqueda de texto
            if search_text:
                filtered = []
                for payment in all_payments:
                    # Buscar en descripción, monto, tipo
                    if (search_text in payment.description.lower() if payment.description else False or
                        search_text in str(payment.amount) or
                        search_text in payment.payment_type.lower()):
                        filtered.append(payment)
                    else:
                        # Buscar en nombre del inquilino
                        try:
                            tenant = self.tenant_service.get_by_id(payment.tenant_id)
                            if tenant and search_text in tenant.name.lower():
                                filtered.append(payment)
                        except:
                            pass
                all_payments = filtered
            
            # Aplicar ordenamiento
            if sort_by == "Fecha (Desc)":
                all_payments.sort(key=lambda p: p.date, reverse=True)
            elif sort_by == "Fecha (Asc)":
                all_payments.sort(key=lambda p: p.date)
            elif sort_by == "Monto (Desc)":
                all_payments.sort(key=lambda p: p.amount, reverse=True)
            elif sort_by == "Monto (Asc)":
                all_payments.sort(key=lambda p: p.amount)
            elif sort_by == "Inquilino":
                all_payments.sort(key=lambda p: self._get_tenant_name(p.tenant_id))

            self.filtered_payments = all_payments
            self._update_table()
            
        except Exception as e:
            print(f"Error al aplicar filtros: {e}")
            messagebox.showerror("Error", f"Error al filtrar datos: {e}")

    def _get_tenant_name(self, tenant_id):
        """Obtiene el nombre del inquilino."""
        try:
            tenant = self.tenant_service.get_by_id(tenant_id)
            return tenant.name if tenant else "Desconocido"
        except:
            return "Desconocido"

    def _clear_search(self):
        """Limpia la búsqueda y filtros."""
        self.search_var.set("")
        self.status_filter.set("Todos")
        self.type_filter.set("Todos")
        self.sort_var.set("Fecha (Desc)")
        self.start_date.set("")
        self.end_date.set("")
        self._apply_filters()

    def _on_select_payment(self, data: Dict[str, Any]):
        """Maneja la selección de un pago."""
        if data and "id" in data:
            self.current_payment = self.payment_service.get_by_id(int(data["id"]))
        else:
            self.current_payment = None

    def _show_payment_details(self, data: Dict[str, Any]):
        """Muestra los detalles del pago seleccionado."""
        if data and "id" in data:
            payment = self.payment_service.get_by_id(int(data["id"]))
            if payment:
                tenant = self.tenant_service.get_by_id(payment.tenant_id)
                tenant_name = tenant.name if tenant else "Desconocido"
                
                details = f"""
DETALLES DEL PAGO

Inquilino: {tenant_name}
Fecha: {payment.date.strftime('%d/%m/%Y')}
Monto: ${payment.amount:,.2f}
Tipo: {payment.payment_type}
Estado: {payment.status}
Descripción: {payment.description or 'Sin descripción'}
Fecha de Vencimiento: {payment.due_date.strftime('%d/%m/%Y') if payment.due_date else 'No especificada'}
"""
                messagebox.showinfo("Detalles del Pago", details)

    def _export_data(self):
        """Exporta los datos actuales a CSV."""
        if not self.filtered_payments:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar datos de pagos"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = ["Fecha", "Inquilino", "Monto", "Tipo", "Estado", "Descripción"]
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for payment in self.filtered_payments:
                        tenant_name = self._get_tenant_name(payment.tenant_id)
                        row = [
                            payment.date.strftime("%d/%m/%Y"),
                            tenant_name,
                            f"${payment.amount:,.2f}",
                            payment.payment_type,
                            payment.status,
                            payment.description or ""
                        ]
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar datos: {e}")

    def _refresh_data(self):
        """Actualiza los datos de la tabla."""
        self._load_data()

    def _go_back_to_payments_dashboard(self):
        """Vuelve al dashboard de pagos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_dashboard')

    def refresh(self):
        """Actualiza la vista."""
        self._refresh_data() 