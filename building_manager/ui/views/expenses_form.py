import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date
import os
import shutil

from ...models.expense import Expense
from ...services.expense_service import ExpenseService
from ..components import BaseForm


class ExpenseFormView(ttk.Frame):
    """Formulario avanzado para registrar y editar gastos con adjuntos."""
    
    def __init__(self, master: Any, expense: Optional[Expense] = None):
        super().__init__(master)
        self.expense_service = ExpenseService()
        self.expense = expense
        self.attached_files: List[str] = []
        self.is_editing = expense is not None
        
        self._setup_ui()
        if self.expense:
            self._load_expense_data()

    def _setup_ui(self):
        """Configura la interfaz del formulario de gastos."""
        self.configure(padding="16")

        # HEADER CON TÍTULO
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 16))
        
        # Título principal
        title_text = "✏️ Editar Gasto" if self.is_editing else "💰 Nuevo Gasto"
        main_title = ttk.Label(
            header_frame,
            text=title_text,
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            header_frame,
            text="Complete todos los campos obligatorios",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        subtitle.pack()

        # INFORMACIÓN BÁSICA DEL GASTO
        basic_frame = ttk.LabelFrame(self, text="📋 Información Básica", padding="12")
        basic_frame.pack(fill=tk.X, pady=(0, 12))

        # Primera fila: descripción y categoría
        row1 = ttk.Frame(basic_frame)
        row1.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(row1, text="* Descripción:").pack(side=tk.LEFT, padx=(0, 5))
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(
            row1,
            textvariable=self.description_var,
            width=35,
            font=("Segoe UI", 10)
        )
        self.description_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(row1, text="* Categoría:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            row1,
            textvariable=self.category_var,
            values=[
                "Mantenimiento",
                "Servicios",
                "Reparaciones",
                "Impuestos",
                "Seguros",
                "Limpieza",
                "Personal",
                "Suministros",
                "Otro"
            ],
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.LEFT)

        # Segunda fila: monto y fecha
        row2 = ttk.Frame(basic_frame)
        row2.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(row2, text="* Monto:").pack(side=tk.LEFT, padx=(0, 5))
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(
            row2,
            textvariable=self.amount_var,
            width=15,
            font=("Segoe UI", 10)
        )
        self.amount_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(row2, text="* Fecha:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        self.date_entry = ttk.Entry(
            row2,
            textvariable=self.date_var,
            width=12,
            font=("Segoe UI", 10)
        )
        self.date_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(row2, text="Estado:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="Pagado")
        self.status_combo = ttk.Combobox(
            row2,
            textvariable=self.status_var,
            values=["Pagado", "Pendiente", "Anulado"],
            state="readonly",
            width=12
        )
        self.status_combo.pack(side=tk.LEFT)

        # INFORMACIÓN DE PROVEEDOR Y PAGO
        provider_frame = ttk.LabelFrame(self, text="🏢 Información de Proveedor", padding="12")
        provider_frame.pack(fill=tk.X, pady=(0, 12))

        # Fila de proveedor
        prov_row1 = ttk.Frame(provider_frame)
        prov_row1.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(prov_row1, text="Proveedor:").pack(side=tk.LEFT, padx=(0, 5))
        self.provider_var = tk.StringVar()
        self.provider_entry = ttk.Entry(
            prov_row1,
            textvariable=self.provider_var,
            width=30,
            font=("Segoe UI", 10)
        )
        self.provider_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(prov_row1, text="N° Factura:").pack(side=tk.LEFT, padx=(0, 5))
        self.invoice_var = tk.StringVar()
        self.invoice_entry = ttk.Entry(
            prov_row1,
            textvariable=self.invoice_var,
            width=20,
            font=("Segoe UI", 10)
        )
        self.invoice_entry.pack(side=tk.LEFT)

        # Fila de método de pago
        prov_row2 = ttk.Frame(provider_frame)
        prov_row2.pack(fill=tk.X)

        ttk.Label(prov_row2, text="Método de Pago:").pack(side=tk.LEFT, padx=(0, 5))
        self.payment_method_var = tk.StringVar(value="Transferencia")
        self.payment_method_combo = ttk.Combobox(
            prov_row2,
            textvariable=self.payment_method_var,
            values=["Efectivo", "Transferencia", "Tarjeta", "Cheque", "Otro"],
            state="readonly",
            width=15
        )
        self.payment_method_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Checkbox recurrente
        self.is_recurring_var = tk.BooleanVar()
        self.recurring_check = ttk.Checkbutton(
            prov_row2,
            text="Gasto Recurrente",
            variable=self.is_recurring_var,
            command=self._on_recurring_change
        )
        self.recurring_check.pack(side=tk.LEFT, padx=(0, 15))

        # Período de recurrencia (inicialmente oculto)
        ttk.Label(prov_row2, text="Período:").pack(side=tk.LEFT, padx=(0, 5))
        self.recurrence_var = tk.StringVar()
        self.recurrence_combo = ttk.Combobox(
            prov_row2,
            textvariable=self.recurrence_var,
            values=["Mensual", "Trimestral", "Anual"],
            state="readonly",
            width=12
        )
        self.recurrence_combo.pack(side=tk.LEFT)
        self.recurrence_combo.configure(state="disabled")

        # DISTRIBUCIÓN POR APARTAMENTOS (NUEVA FUNCIONALIDAD)
        apartment_frame = ttk.LabelFrame(self, text="🏠 Distribución por Apartamentos", padding="12")
        apartment_frame.pack(fill=tk.X, pady=(0, 12))

        # Tipo de distribución
        dist_row1 = ttk.Frame(apartment_frame)
        dist_row1.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(dist_row1, text="Tipo de distribución:").pack(side=tk.LEFT, padx=(0, 5))
        self.distribution_type_var = tk.StringVar(value="General")
        self.distribution_combo = ttk.Combobox(
            dist_row1,
            textvariable=self.distribution_type_var,
            values=["General", "Por apartamento específico", "Dividir entre todos"],
            state="readonly",
            width=25
        )
        self.distribution_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.distribution_combo.bind("<<ComboboxSelected>>", self._on_distribution_change)

        # Campo de apartamento específico (inicialmente oculto)
        self.specific_apartment_var = tk.StringVar()
        self.apartment_label = ttk.Label(dist_row1, text="Apartamento:")
        self.apartment_entry = ttk.Entry(
            dist_row1,
            textvariable=self.specific_apartment_var,
            width=10
        )

        # ADJUNTOS Y SOPORTES
        attachments_frame = ttk.LabelFrame(self, text="📎 Adjuntos y Soportes", padding="12")
        attachments_frame.pack(fill=tk.X, pady=(0, 12))

        # Botones de adjuntos
        attach_row = ttk.Frame(attachments_frame)
        attach_row.pack(fill=tk.X, pady=(0, 8))

        attach_btn = ttk.Button(
            attach_row,
            text="📁 Adjuntar Archivo",
            command=self._attach_file,
            bootstyle="info"
        )
        attach_btn.pack(side=tk.LEFT, padx=(0, 8))

        remove_btn = ttk.Button(
            attach_row,
            text="🗑️ Eliminar Seleccionado",
            command=self._remove_attachment,
            bootstyle="outline-danger"
        )
        remove_btn.pack(side=tk.LEFT, padx=(0, 8))

        view_btn = ttk.Button(
            attach_row,
            text="👁️ Ver Archivo",
            command=self._view_attachment,
            bootstyle="outline-info"
        )
        view_btn.pack(side=tk.LEFT)

        # Lista de archivos adjuntos
        self.attachments_list = tk.Listbox(
            attachments_frame,
            height=4,
            font=("Segoe UI", 9)
        )
        self.attachments_list.pack(fill=tk.X, pady=(5, 0))

        # NOTAS ADICIONALES
        notes_frame = ttk.LabelFrame(self, text="📝 Notas Adicionales", padding="12")
        notes_frame.pack(fill=tk.X, pady=(0, 16))

        self.notes_text = tk.Text(
            notes_frame,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.notes_text.pack(fill=tk.X)

        # BOTONES DE ACCIÓN
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X)

        # Botones del lado izquierdo
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.pack(side=tk.LEFT)

        preview_btn = ttk.Button(
            left_buttons,
            text="👁️ Vista Previa",
            command=self._preview_expense,
            bootstyle="outline-info"
        )
        preview_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Botones del lado derecho
        right_buttons = ttk.Frame(buttons_frame)
        right_buttons.pack(side=tk.RIGHT)

        cancel_btn = ttk.Button(
            right_buttons,
            text="❌ Cancelar",
            command=self._cancel,
            bootstyle="outline-secondary"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))

        save_text = "💾 Actualizar" if self.is_editing else "💾 Guardar"
        save_btn = ttk.Button(
            right_buttons,
            text=save_text,
            command=self._save_expense,
            bootstyle="success"
        )
        save_btn.pack(side=tk.RIGHT)

        # INFORMACIÓN DE AYUDA
        help_text = "* Campos obligatorios | Formatos: DD/MM/YYYY para fecha, números con punto decimal para montos"
        help_label = ttk.Label(
            self,
            text=help_text,
            font=("Segoe UI", 8),
            bootstyle="secondary"
        )
        help_label.pack(pady=(8, 0))

    def _on_recurring_change(self):
        """Maneja el cambio en el checkbox de recurrente."""
        if self.is_recurring_var.get():
            self.recurrence_combo.configure(state="readonly")
            self.recurrence_var.set("Mensual")
        else:
            self.recurrence_combo.configure(state="disabled")
            self.recurrence_var.set("")

    def _on_distribution_change(self, event=None):
        """Maneja el cambio en el tipo de distribución."""
        dist_type = self.distribution_type_var.get()
        
        if dist_type == "Por apartamento específico":
            self.apartment_label.pack(side=tk.LEFT, padx=(15, 5))
            self.apartment_entry.pack(side=tk.LEFT)
        else:
            self.apartment_label.pack_forget()
            self.apartment_entry.pack_forget()
            self.specific_apartment_var.set("")

    def _attach_file(self):
        """Adjunta un archivo al gasto."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo adjunto",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PDF", "*.pdf"),
                ("Excel", "*.xlsx *.xls"),
                ("Word", "*.docx *.doc"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if filename:
            # Crear directorio de adjuntos si no existe
            attachments_dir = "attachments/expenses"
            os.makedirs(attachments_dir, exist_ok=True)
            
            # Copiar archivo a directorio de adjuntos
            file_basename = os.path.basename(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{file_basename}"
            dest_path = os.path.join(attachments_dir, new_filename)
            
            try:
                shutil.copy2(filename, dest_path)
                self.attached_files.append(dest_path)
                self._update_attachments_list()
                messagebox.showinfo("Éxito", f"Archivo adjuntado: {file_basename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al adjuntar archivo: {e}")

    def _remove_attachment(self):
        """Elimina el adjunto seleccionado."""
        selection = self.attachments_list.curselection()
        if selection:
            index = selection[0]
            removed_file = self.attached_files.pop(index)
            
            # Eliminar archivo físico si es posible
            try:
                if os.path.exists(removed_file):
                    os.remove(removed_file)
            except Exception:
                pass  # Si no se puede eliminar, continuar
            
            self._update_attachments_list()
            messagebox.showinfo("Eliminado", "Archivo adjunto eliminado.")
        else:
            messagebox.showwarning("Selección", "Seleccione un archivo para eliminar.")

    def _view_attachment(self):
        """Ve el adjunto seleccionado."""
        selection = self.attachments_list.curselection()
        if selection:
            index = selection[0]
            file_path = self.attached_files[index]
            
            if os.path.exists(file_path):
                try:
                    # Abrir archivo con aplicación predeterminada del sistema
                    os.startfile(file_path)  # Windows
                except Exception:
                    try:
                        os.system(f"open '{file_path}'")  # macOS
                    except Exception:
                        try:
                            os.system(f"xdg-open '{file_path}'")  # Linux
                        except Exception:
                            messagebox.showerror("Error", "No se pudo abrir el archivo.")
            else:
                messagebox.showerror("Error", "El archivo no existe.")
        else:
            messagebox.showwarning("Selección", "Seleccione un archivo para ver.")

    def _update_attachments_list(self):
        """Actualiza la lista de adjuntos."""
        self.attachments_list.delete(0, tk.END)
        for file_path in self.attached_files:
            filename = os.path.basename(file_path)
            file_size = self._get_file_size(file_path)
            self.attachments_list.insert(tk.END, f"{filename} ({file_size})")

    def _get_file_size(self, file_path):
        """Obtiene el tamaño del archivo en formato legible."""
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except Exception:
            return "Tamaño desconocido"

    def _preview_expense(self):
        """Muestra una vista previa del gasto."""
        try:
            data = self._collect_form_data()
            
            preview_text = f"""
VISTA PREVIA DEL GASTO

Descripción: {data['description']}
Monto: ${data['amount']:,.2f}
Fecha: {data['date'].strftime('%d/%m/%Y')}
Categoría: {data['category']}
Estado: {data['status']}
Proveedor: {data.get('provider', 'No especificado')}
N° Factura: {data.get('invoice_number', 'No especificado')}
Método de Pago: {data.get('payment_method', 'No especificado')}
Recurrente: {'Sí (' + data.get('recurrence_period', '') + ')' if data.get('is_recurring') else 'No'}
Distribución: {data.get('distribution_type', 'General')}
{f'Apartamento específico: {data.get("specific_apartment", "")}' if data.get('specific_apartment') else ''}
Adjuntos: {len(self.attached_files)} archivo(s)
"""
            
            preview_window = tk.Toplevel(self)
            preview_window.title("Vista Previa del Gasto")
            preview_window.geometry("400x350")
            preview_window.transient(self)
            
            text_widget = tk.Text(preview_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, preview_text)
            text_widget.configure(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar vista previa: {e}")

    def _collect_form_data(self):
        """Recolecta y valida los datos del formulario."""
        # Validar campos obligatorios
        if not self.description_var.get().strip():
            raise ValueError("La descripción es obligatoria")
        
        if not self.amount_var.get().strip():
            raise ValueError("El monto es obligatorio")
        
        if not self.category_var.get():
            raise ValueError("La categoría es obligatoria")
        
        # Validar y convertir monto
        try:
            amount = Decimal(self.amount_var.get().replace(',', ''))
            if amount <= 0:
                raise ValueError("El monto debe ser mayor a cero")
        except (ValueError, Exception):
            raise ValueError("El monto debe ser un número válido")
        
        # Validar y convertir fecha
        try:
            date_str = self.date_var.get().strip()
            if '/' in date_str:
                expense_date = datetime.strptime(date_str, "%d/%m/%Y").date()
            else:
                expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use DD/MM/YYYY")
        
        # Recopilar todos los datos
        data = {
            'description': self.description_var.get().strip(),
            'amount': amount,
            'date': expense_date,
            'category': self.category_var.get(),
            'status': self.status_var.get(),
            'provider': self.provider_var.get().strip() or None,
            'invoice_number': self.invoice_var.get().strip() or None,
            'payment_method': self.payment_method_var.get(),
            'is_recurring': self.is_recurring_var.get(),
            'recurrence_period': self.recurrence_var.get() if self.is_recurring_var.get() else None,
            'distribution_type': self.distribution_type_var.get(),
            'specific_apartment': self.specific_apartment_var.get().strip() or None,
            'notes': self.notes_text.get(1.0, tk.END).strip() or None
        }
        
        return data

    def _save_expense(self):
        """Guarda el gasto."""
        try:
            data = self._collect_form_data()
            
            # Crear objeto Expense
            expense_data = {
                'id': self.expense.id if self.is_editing else None,
                'description': data['description'],
                'amount': data['amount'],
                'date': data['date'],
                'category': data['category'],
                'provider': data['provider'],
                'invoice_number': data['invoice_number'],
                'payment_method': data['payment_method'],
                'is_recurring': data['is_recurring'],
                'recurrence_period': data['recurrence_period'],
                'status': data['status']
            }
            
            expense = Expense(**expense_data)
            
            # Guardar en la base de datos
            if self.is_editing:
                success = self.expense_service.update(self.expense.id, expense)
                if success:
                    messagebox.showinfo("Éxito", "Gasto actualizado correctamente")
                else:
                    raise Exception("Error al actualizar el gasto")
            else:
                expense_id = self.expense_service.register_expense(expense)
                if expense_id:
                    messagebox.showinfo("Éxito", f"Gasto registrado correctamente (ID: {expense_id})")
                else:
                    raise Exception("Error al registrar el gasto")
            
            # Regresar a la vista anterior
            self._go_back()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_expense_data(self):
        """Carga los datos del gasto en edición."""
        if not self.expense:
            return
        
        self.description_var.set(self.expense.description)
        self.amount_var.set(str(self.expense.amount))
        self.date_var.set(self.expense.date.strftime("%d/%m/%Y"))
        self.category_var.set(self.expense.category)
        self.status_var.set(self.expense.status)
        self.provider_var.set(self.expense.provider or "")
        self.invoice_var.set(self.expense.invoice_number or "")
        self.payment_method_var.set(getattr(self.expense, 'payment_method', 'Transferencia'))
        
        # Datos de recurrencia
        if getattr(self.expense, 'is_recurring', False):
            self.is_recurring_var.set(True)
            self.recurrence_var.set(getattr(self.expense, 'recurrence_period', 'Mensual'))
            self.recurrence_combo.configure(state="readonly")

    def _cancel(self):
        """Cancela la edición/creación."""
        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar? Se perderán los cambios no guardados."):
            self._go_back()

    def _go_back(self):
        """Vuelve a la vista anterior."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_dashboard')

    def refresh(self):
        """Actualiza la vista."""
        pass 