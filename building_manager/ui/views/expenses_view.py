import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any

from ..components import DataTable, BaseForm
from ...services import ExpenseService
from ...models import Expense

class ExpenseForm(BaseForm):
    """Formulario para registrar gastos."""
    def __init__(
        self,
        master: Any,
        on_submit: callable,
        on_cancel: callable,
        expense: Optional[Expense] = None
    ):
        super().__init__(
            master,
            on_submit=on_submit,
            on_cancel=on_cancel
        )
        
        self._setup_fields()
        if expense:
            self.set_data(expense.to_dict())

    def _setup_fields(self):
        """Configura los campos del formulario."""
        self.add_field("description", "Descripción")
        self.add_field("amount", "Monto", field_type="number")
        self.add_field("date", "Fecha", field_type="date")
        self.add_field(
            "category",
            "Categoría",
            field_type="combobox",
            values=[
                "Mantenimiento",
                "Servicios",
                "Impuestos",
                "Seguros",
                "Personal",
                "Suministros",
                "Otro"
            ]
        )
        self.add_field(
            "payment_method",
            "Método de Pago",
            field_type="combobox",
            values=["Efectivo", "Transferencia", "Tarjeta", "Otro"]
        )
        self.add_field(
            "status",
            "Estado",
            field_type="combobox",
            values=["Completado", "Pendiente", "Anulado"]
        )
        self.add_field(
            "is_recurring",
            "Recurrente",
            field_type="combobox",
            values=["No", "Mensual", "Trimestral", "Anual"]
        )
        self.add_field("provider", "Proveedor", required=False)
        self.add_field("invoice_number", "Número de Factura", required=False)
        self.add_field("notes", "Notas", required=False)

class ExpensesView(ttk.Frame):
    """Vista para gestionar gastos."""
    def __init__(self, master: Any):
        super().__init__(master)
        self.expense_service = ExpenseService()
        self.current_expense: Optional[Expense] = None
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de la vista."""
        # Contenedor principal con padding
        self.configure(padding="20")

        # Frame superior con acciones
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill=tk.X, pady=(0, 20))

        # Botón para registrar gasto
        add_btn = ttk.Button(
            actions_frame,
            text="Registrar Gasto",
            command=self._show_form,
            bootstyle="primary"
        )
        add_btn.pack(side=tk.LEFT)

        # Tabla de gastos
        self.table = DataTable(
            self,
            columns=[
                ("date", "Fecha"),
                ("description", "Descripción"),
                ("category", "Categoría"),
                ("amount", "Monto"),
                ("status", "Estado"),
                ("is_recurring", "Recurrente")
            ],
            on_select=self._on_select_expense,
            on_double_click=self._show_form
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _load_data(self):
        """Carga los datos de gastos."""
        expenses = self.expense_service.get_all()
        
        # Preparar datos para la tabla
        data = [
            {
                "id": expense.id,
                "date": expense.date.strftime("%d/%m/%Y"),
                "description": expense.description,
                "category": expense.category,
                "amount": f"${expense.amount:,.2f}",
                "status": expense.status,
                "is_recurring": expense.is_recurring
            }
            for expense in expenses
        ]
        self.table.set_data(data)

    def _on_select_expense(self, data: Dict[str, Any]):
        """Maneja la selección de un gasto."""
        if data and "id" in data:
            self.current_expense = self.expense_service.get_by_id(int(data["id"]))
        else:
            self.current_expense = None

    def _show_form(self, data: Optional[Dict[str, Any]] = None):
        """Muestra el formulario de gasto."""
        # Crear ventana modal
        dialog = ttk.Toplevel(self)
        dialog.title("Gasto")
        dialog.geometry("400x600")
        dialog.transient(self)
        dialog.grab_set()

        # Determinar el gasto a editar
        expense = None
        if data and "id" in data:
            expense = self.expense_service.get_by_id(int(data["id"]))
        elif self.current_expense:
            expense = self.current_expense

        # Crear y mostrar el formulario
        form = ExpenseForm(
            dialog,
            on_submit=lambda values: self._handle_submit(values, dialog),
            on_cancel=dialog.destroy,
            expense=expense
        )
        form.pack(fill=tk.BOTH, expand=True)

    def _handle_submit(self, values: Dict[str, Any], dialog: ttk.Toplevel):
        """Maneja el envío del formulario."""
        try:
            # Convertir valores
            values["amount"] = Decimal(values["amount"])
            values["is_recurring"] = values["is_recurring"] != "No"
            
            # Crear o actualizar gasto
            if self.current_expense:
                expense = Expense(**values)
                self.expense_service.update(self.current_expense.id, expense)
                messagebox.showinfo(
                    "Éxito",
                    "Gasto actualizado correctamente"
                )
            else:
                expense = Expense(**values)
                self.expense_service.register_expense(expense)
                messagebox.showinfo(
                    "Éxito",
                    "Gasto registrado correctamente"
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

    def refresh(self):
        """Actualiza los datos de la vista."""
        self._load_data() 