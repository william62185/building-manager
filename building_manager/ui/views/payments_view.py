import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any

from ..components import DataTable, BaseForm
from ...services import PaymentService, TenantService
from ...models import Payment, Tenant

class PaymentForm(BaseForm):
    """Formulario para registrar pagos."""
    def __init__(
        self,
        master: Any,
        tenants: list[Tenant],
        on_submit: callable,
        on_cancel: callable,
        payment: Optional[Payment] = None
    ):
        super().__init__(
            master,
            on_submit=on_submit,
            on_cancel=on_cancel
        )
        
        self.tenants = {str(t.id): t.name for t in tenants}
        self._setup_fields()
        if payment:
            self.set_values(payment.to_dict())

    def _setup_fields(self):
        """Configura los campos del formulario."""
        self.add_field(
            "tenant_id",
            "Inquilino",
            field_type="combobox",
            values=list(self.tenants.values())
        )
        self.add_field("amount", "Monto", field_type="number")
        self.add_field("date", "Fecha", field_type="date")
        self.add_field(
            "payment_type",
            "Tipo de Pago",
            field_type="combobox",
            values=["Efectivo", "Transferencia", "Tarjeta", "Otro"]
        )
        self.add_field("description", "Descripción", required=False)
        self.add_field(
            "status",
            "Estado",
            field_type="combobox",
            values=["Completado", "Pendiente", "Anulado"]
        )

    def get_values(self) -> Dict[str, Any]:
        """Obtiene los valores del formulario."""
        values = super().get_values()
        
        # Convertir nombre del inquilino a ID
        tenant_name = values["tenant_id"]
        tenant_id = next(
            (k for k, v in self.tenants.items() if v == tenant_name),
            None
        )
        values["tenant_id"] = int(tenant_id) if tenant_id else None
        
        return values

    def set_values(self, values: Dict[str, Any]):
        """Establece los valores en el formulario."""
        # Convertir ID del inquilino a nombre
        if "tenant_id" in values:
            tenant_id = str(values["tenant_id"])
            values["tenant_id"] = self.tenants.get(tenant_id, "")
        
        super().set_values(values)

class PaymentsView(ttk.Frame):
    """Vista para gestionar pagos."""
    def __init__(self, master: Any):
        super().__init__(master)
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        self.current_payment: Optional[Payment] = None
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de la vista."""
        # Contenedor principal con padding
        self.configure(padding="20")

        # Frame superior con título y navegación
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="📝 Registro de Pagos",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Formulario para registrar nuevos pagos",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        subtitle.pack()
        
        # Botón para ir al Dashboard de Pagos
        dashboard_btn = ttk.Button(
            header_frame,
            text="🏠 Dashboard de Pagos",
            command=self._go_to_payments_dashboard,
            bootstyle="outline-info"
        )
        dashboard_btn.pack(side=tk.RIGHT)

        # Frame superior con acciones
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X, pady=(0, 20))

        # Botón para registrar pago
        add_btn = ttk.Button(
            actions_frame,
            text="💵 Registrar Nuevo Pago",
            command=self._show_form,
            bootstyle="primary"
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para actualizar tabla
        refresh_btn = ttk.Button(
            actions_frame,
            text="🔄 Actualizar",
            command=self._load_data,
            bootstyle="outline-secondary"
        )
        refresh_btn.pack(side=tk.LEFT)

        # Tabla de pagos
        self.table = DataTable(
            self,
            columns=[
                ("date", "Fecha"),
                ("tenant", "Inquilino"),
                ("amount", "Monto"),
                ("payment_type", "Tipo"),
                ("status", "Estado")
            ],
            on_select=self._on_select_payment,
            on_double_click=self._show_form
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _load_data(self):
        """Carga los datos de pagos."""
        payments = self.payment_service.get_all()
        tenants = {t.id: t for t in self.tenant_service.get_all()}
        
        # Preparar datos para la tabla
        data = [
            {
                "id": payment.id,
                "date": payment.date.strftime("%d/%m/%Y"),
                "tenant": tenants[payment.tenant_id].name if payment.tenant_id in tenants else "N/A",
                "amount": f"${payment.amount:,.2f}",
                "payment_type": payment.payment_type,
                "status": payment.status
            }
            for payment in payments
        ]
        self.table.set_data(data)

    def _on_select_payment(self, data: Dict[str, Any]):
        """Maneja la selección de un pago."""
        if data and "id" in data:
            self.current_payment = self.payment_service.get_by_id(int(data["id"]))
        else:
            self.current_payment = None

    def _show_form(self, data: Optional[Dict[str, Any]] = None):
        """Muestra el formulario de pago."""
        # Crear ventana modal
        dialog = ttk.Toplevel(self)
        dialog.title("Pago")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()

        # Obtener inquilinos activos
        tenants = self.tenant_service.get_active_tenants()

        # Determinar el pago a editar
        payment = None
        if data and "id" in data:
            payment = self.payment_service.get_by_id(int(data["id"]))
        elif self.current_payment:
            payment = self.current_payment

        # Crear y mostrar el formulario
        form = PaymentForm(
            dialog,
            tenants=tenants,
            on_submit=lambda values: self._handle_submit(values, dialog),
            on_cancel=dialog.destroy,
            payment=payment
        )
        form.pack(fill=tk.BOTH, expand=True)

    def _handle_submit(self, values: Dict[str, Any], dialog: ttk.Toplevel):
        """Maneja el envío del formulario."""
        try:
            # Validar inquilino
            if not values["tenant_id"]:
                raise ValueError("Debe seleccionar un inquilino")

            # Convertir valores
            values["amount"] = Decimal(values["amount"])
            
            # Crear o actualizar pago
            if self.current_payment:
                payment = Payment(**values)
                self.payment_service.update(self.current_payment.id, payment)
                messagebox.showinfo(
                    "Éxito",
                    "Pago actualizado correctamente"
                )
            else:
                payment = Payment(**values)
                self.payment_service.register_payment(payment)
                messagebox.showinfo(
                    "Éxito",
                    "Pago registrado correctamente"
                )

            # Cerrar formulario y actualizar datos
            dialog.destroy()
            self._load_data()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror(
                "Error",
                "Ocurrió un error al procesar el formulario"
            )

    def _go_to_payments_dashboard(self):
        """Navega al Dashboard de Pagos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_dashboard')

    def refresh(self):
        """Actualiza los datos de la vista."""
        self._load_data() 