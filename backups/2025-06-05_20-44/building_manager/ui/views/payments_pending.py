import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date, timedelta

from ...models.payment import Payment
from ...services.payment_service import PaymentService
from ...services.tenant_service import TenantService
from ..components import DataTable, MetricsCard


class PaymentsPendingView(ttk.Frame):
    """Vista de gestión de pagos pendientes con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        self.pending_payments: List[Payment] = []
        self.current_payment: Optional[Payment] = None
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de pagos pendientes."""
        self.configure(padding="12")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="📋 Pagos Pendientes",
            font=("Segoe UI", 18, "bold"),
            bootstyle="danger"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Gestión de pagos por recibir y morosos",
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

        # RESUMEN DE PAGOS PENDIENTES (4 cards horizontales)
        metrics_section = ttk.LabelFrame(self, text="⚠️ Resumen de Pendientes", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 12))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas de pendientes
        self.total_pending = MetricsCard(
            all_metrics,
            title="Total Pendientes",
            value="0",
            subtitle="Pagos sin recibir",
            icon="⏰",
            color="warning"
        )
        self.total_pending.pack(side=tk.LEFT, expand=True, padx=2)

        self.amount_pending = MetricsCard(
            all_metrics,
            title="Monto Pendiente",
            value="$0.00",
            subtitle="Dinero por cobrar",
            icon="💸",
            color="danger"
        )
        self.amount_pending.pack(side=tk.LEFT, expand=True, padx=2)

        self.overdue_payments = MetricsCard(
            all_metrics,
            title="Pagos Vencidos",
            value="0",
            subtitle="Después de fecha límite",
            icon="🚨",
            color="danger"
        )
        self.overdue_payments.pack(side=tk.LEFT, expand=True, padx=2)

        self.upcoming_payments = MetricsCard(
            all_metrics,
            title="Próximos a Vencer",
            value="0",
            subtitle="En los próximos 7 días",
            icon="⌛",
            color="info"
        )
        self.upcoming_payments.pack(side=tk.LEFT, expand=True, padx=2)

        # FILTROS Y ACCIONES
        filter_frame = ttk.LabelFrame(self, text="🔧 Filtros y Acciones", padding="12")
        filter_frame.pack(fill=tk.X, pady=(0, 12))

        # Primera fila: filtros
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_row1, text="Mostrar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_type = tk.StringVar(value="Todos los pendientes")
        filter_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.filter_type,
            values=[
                "Todos los pendientes",
                "Solo vencidos",
                "Próximos a vencer (7 días)",
                "Renta pendiente",
                "Servicios pendientes"
            ],
            state="readonly",
            width=25
        )
        filter_combo.pack(side=tk.LEFT, padx=(0, 15))
        filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(filter_row1, text="Ordenar por:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="Fecha vencimiento")
        sort_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.sort_var,
            values=["Fecha vencimiento", "Monto (Mayor)", "Inquilino", "Días vencido"],
            state="readonly",
            width=15
        )
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Segunda fila: acciones
        actions_row = ttk.Frame(filter_frame)
        actions_row.pack(fill=tk.X)

        # Botones de acción masiva
        mass_actions_frame = ttk.Frame(actions_row)
        mass_actions_frame.pack(side=tk.LEFT)

        mark_paid_btn = ttk.Button(
            mass_actions_frame,
            text="✅ Marcar como Pagado",
            command=self._mark_as_paid,
            bootstyle="success"
        )
        mark_paid_btn.pack(side=tk.LEFT, padx=(0, 8))

        send_reminder_btn = ttk.Button(
            mass_actions_frame,
            text="📧 Enviar Recordatorio",
            command=self._send_reminder,
            bootstyle="warning"
        )
        send_reminder_btn.pack(side=tk.LEFT, padx=(0, 8))

        generate_report_btn = ttk.Button(
            mass_actions_frame,
            text="📄 Generar Reporte",
            command=self._generate_pending_report,
            bootstyle="info"
        )
        generate_report_btn.pack(side=tk.LEFT)

        # Botón de actualizar
        refresh_btn = ttk.Button(
            actions_row,
            text="🔄 Actualizar",
            command=self._refresh_data,
            bootstyle="primary"
        )
        refresh_btn.pack(side=tk.RIGHT)

        # TABLA DE PAGOS PENDIENTES
        table_frame = ttk.LabelFrame(self, text="📋 Lista de Pagos Pendientes", padding="8")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Contador de registros
        self.records_label = ttk.Label(table_frame, text="0 pagos pendientes")
        self.records_label.pack(anchor=tk.W, pady=(0, 5))

        # Tabla de pagos pendientes
        self.table = DataTable(
            table_frame,
            columns=[
                ("tenant_name", "Inquilino"),
                ("due_date", "Fecha Límite"),
                ("days_overdue", "Días Vencido"),
                ("amount", "Monto"),
                ("payment_type", "Tipo"),
                ("status_detail", "Estado Detallado"),
                ("description", "Descripción")
            ],
            on_select=self._on_select_payment,
            on_double_click=lambda data: self._show_payment_details(data)
        )
        self.table.pack(fill=tk.BOTH, expand=True)

        # PANEL DE DETALLES DEL PAGO SELECCIONADO
        details_frame = ttk.LabelFrame(self, text="ℹ️ Detalles del Pago Seleccionado", padding="12")
        details_frame.pack(fill=tk.X, pady=(12, 0))

        self.details_text = tk.Text(
            details_frame,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.X)

    def _load_data(self):
        """Carga los pagos pendientes."""
        try:
            # Obtener todos los pagos pendientes
            all_payments = self.payment_service.get_all()
            self.pending_payments = [p for p in all_payments if p.status in ["Pendiente", "Vencido"]]
            
            self._apply_filters()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pagos pendientes: {e}")

    def _apply_filters(self):
        """Aplica los filtros seleccionados."""
        try:
            filter_type = self.filter_type.get()
            sort_by = self.sort_var.get()
            today = date.today()
            
            # Aplicar filtros
            filtered_payments = []
            
            for payment in self.pending_payments:
                include = False
                
                if filter_type == "Todos los pendientes":
                    include = True
                elif filter_type == "Solo vencidos":
                    include = payment.due_date and payment.due_date < today
                elif filter_type == "Próximos a vencer (7 días)":
                    if payment.due_date:
                        days_until_due = (payment.due_date - today).days
                        include = 0 <= days_until_due <= 7
                elif filter_type == "Renta pendiente":
                    include = payment.payment_type == "Renta"
                elif filter_type == "Servicios pendientes":
                    include = payment.payment_type == "Servicios"
                
                if include:
                    filtered_payments.append(payment)
            
            # Aplicar ordenamiento
            if sort_by == "Fecha vencimiento":
                filtered_payments.sort(key=lambda p: p.due_date or date.max)
            elif sort_by == "Monto (Mayor)":
                filtered_payments.sort(key=lambda p: p.amount, reverse=True)
            elif sort_by == "Inquilino":
                filtered_payments.sort(key=lambda p: self._get_tenant_name(p.tenant_id))
            elif sort_by == "Días vencido":
                filtered_payments.sort(key=lambda p: self._calculate_days_overdue(p), reverse=True)

            self._update_table(filtered_payments)
            
        except Exception as e:
            print(f"Error al aplicar filtros: {e}")

    def _update_table(self, payments):
        """Actualiza la tabla con los pagos filtrados."""
        data = []
        total_amount = Decimal("0")
        overdue_count = 0
        upcoming_count = 0
        today = date.today()
        
        for payment in payments:
            # Obtener nombre del inquilino
            tenant_name = self._get_tenant_name(payment.tenant_id)
            
            # Calcular días vencido
            days_overdue = self._calculate_days_overdue(payment)
            
            # Determinar estado detallado
            status_detail = self._get_status_detail(payment, days_overdue)
            
            data.append({
                "id": payment.id,
                "tenant_name": tenant_name,
                "due_date": payment.due_date.strftime("%d/%m/%Y") if payment.due_date else "Sin fecha",
                "days_overdue": str(days_overdue) if days_overdue > 0 else "No vencido",
                "amount": f"${payment.amount:,.2f}",
                "payment_type": payment.payment_type,
                "status_detail": status_detail,
                "description": payment.description or ""
            })
            
            # Calcular estadísticas
            total_amount += payment.amount
            if days_overdue > 0:
                overdue_count += 1
            elif payment.due_date and (payment.due_date - today).days <= 7:
                upcoming_count += 1
        
        self.table.set_data(data)
        self.records_label.configure(text=f"{len(data)} pago(s) pendiente(s)")
        
        # Actualizar métricas
        self.total_pending.update_value(str(len(payments)))
        self.amount_pending.update_value(f"${total_amount:,.2f}")
        self.overdue_payments.update_value(str(overdue_count))
        self.upcoming_payments.update_value(str(upcoming_count))

    def _get_tenant_name(self, tenant_id):
        """Obtiene el nombre del inquilino."""
        try:
            tenant = self.tenant_service.get_by_id(tenant_id)
            return tenant.name if tenant else "Desconocido"
        except:
            return "Desconocido"

    def _calculate_days_overdue(self, payment):
        """Calcula los días de vencimiento."""
        if not payment.due_date:
            return 0
        today = date.today()
        if payment.due_date < today:
            return (today - payment.due_date).days
        return 0

    def _get_status_detail(self, payment, days_overdue):
        """Obtiene el estado detallado del pago."""
        if days_overdue > 0:
            if days_overdue <= 7:
                return "🟡 Recién vencido"
            elif days_overdue <= 30:
                return "🟠 Moderadamente vencido"
            else:
                return "🔴 Muy vencido"
        else:
            if payment.due_date:
                days_until_due = (payment.due_date - date.today()).days
                if days_until_due <= 3:
                    return "⚡ Vence pronto"
                elif days_until_due <= 7:
                    return "⏰ Próximo a vencer"
                else:
                    return "✅ Al día"
            else:
                return "❓ Sin fecha límite"

    def _on_filter_change(self, event=None):
        """Maneja cambios en los filtros."""
        self._apply_filters()

    def _on_select_payment(self, data: Dict[str, Any]):
        """Maneja la selección de un pago."""
        if data and "id" in data:
            self.current_payment = self.payment_service.get_by_id(int(data["id"]))
            self._update_details_panel()
        else:
            self.current_payment = None
            self._clear_details_panel()

    def _update_details_panel(self):
        """Actualiza el panel de detalles."""
        if not self.current_payment:
            return
        
        tenant = self.tenant_service.get_by_id(self.current_payment.tenant_id)
        tenant_name = tenant.name if tenant else "Desconocido"
        days_overdue = self._calculate_days_overdue(self.current_payment)
        
        details = f"Inquilino: {tenant_name} | "
        details += f"Monto: ${self.current_payment.amount:,.2f} | "
        details += f"Tipo: {self.current_payment.payment_type} | "
        details += f"Fecha límite: {self.current_payment.due_date.strftime('%d/%m/%Y') if self.current_payment.due_date else 'Sin fecha'} | "
        details += f"Días vencido: {days_overdue if days_overdue > 0 else 'No vencido'} | "
        details += f"Descripción: {self.current_payment.description or 'Sin descripción'}"
        
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.configure(state=tk.DISABLED)

    def _clear_details_panel(self):
        """Limpia el panel de detalles."""
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "Selecciona un pago para ver sus detalles...")
        self.details_text.configure(state=tk.DISABLED)

    def _show_payment_details(self, data: Dict[str, Any]):
        """Muestra los detalles completos del pago."""
        if data and "id" in data:
            payment = self.payment_service.get_by_id(int(data["id"]))
            if payment:
                tenant = self.tenant_service.get_by_id(payment.tenant_id)
                tenant_name = tenant.name if tenant else "Desconocido"
                days_overdue = self._calculate_days_overdue(payment)
                
                details = f"""
DETALLES DEL PAGO PENDIENTE

Inquilino: {tenant_name}
Monto: ${payment.amount:,.2f}
Tipo de Pago: {payment.payment_type}
Fecha de Registro: {payment.date.strftime('%d/%m/%Y')}
Fecha Límite: {payment.due_date.strftime('%d/%m/%Y') if payment.due_date else 'No especificada'}
Estado: {payment.status}
Días de Vencimiento: {days_overdue if days_overdue > 0 else 'No vencido'}
Descripción: {payment.description or 'Sin descripción'}

{f"⚠️ ATENCIÓN: Este pago está vencido por {days_overdue} días" if days_overdue > 0 else "✅ Este pago está al día"}
"""
                messagebox.showinfo("Detalles del Pago Pendiente", details)

    def _mark_as_paid(self):
        """Marca el pago seleccionado como pagado."""
        if not self.current_payment:
            messagebox.showwarning("Advertencia", "Selecciona un pago para marcar como pagado.")
            return
        
        result = messagebox.askyesno(
            "Confirmar Pago",
            f"¿Confirmar que se recibió el pago de ${self.current_payment.amount:,.2f}?"
        )
        
        if result:
            try:
                # Actualizar el estado del pago
                self.current_payment.status = "Completado"
                self.payment_service.update(self.current_payment.id, self.current_payment)
                
                messagebox.showinfo("Éxito", "Pago marcado como completado correctamente.")
                self._refresh_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar el pago: {e}")

    def _send_reminder(self):
        """Envía recordatorio de pago."""
        if not self.current_payment:
            messagebox.showwarning("Advertencia", "Selecciona un pago para enviar recordatorio.")
            return
        
        tenant = self.tenant_service.get_by_id(self.current_payment.tenant_id)
        tenant_name = tenant.name if tenant else "Desconocido"
        
        messagebox.showinfo(
            "Recordatorio Enviado",
            f"Recordatorio de pago enviado a {tenant_name}\n\n" +
            "Nota: Esta función enviará un email/SMS en versiones futuras."
        )

    def _generate_pending_report(self):
        """Genera un reporte de pagos pendientes."""
        if not self.pending_payments:
            messagebox.showwarning("Advertencia", "No hay pagos pendientes para el reporte.")
            return
        
        messagebox.showinfo(
            "Reporte Generado",
            f"Reporte de {len(self.pending_payments)} pagos pendientes generado.\n\n" +
            "Nota: En versiones futuras se generará un PDF detallado."
        )

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