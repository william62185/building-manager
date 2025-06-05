import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date

from ...models.expense import Expense
from ...services.expense_service import ExpenseService
from ..components import DataTable, MetricsCard


class ExpensesByApartmentView(ttk.Frame):
    """Vista para gastos separados por apartamentos."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.expense_service = ExpenseService()
        self.current_apartment: Optional[str] = None
        self.apartments_data: Dict[str, List[Expense]] = {}
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de gastos por apartamento."""
        self.configure(padding="12")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="🏠 Gastos por Apartamento",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Distribución y análisis de gastos por unidad residencial",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        subtitle.pack()
        
        # Botón de navegación
        back_btn = ttk.Button(
            header_frame,
            text="← Dashboard Gastos",
            command=self._go_back_to_expenses_dashboard,
            bootstyle="outline-secondary"
        )
        back_btn.pack(side=tk.RIGHT)

        # RESUMEN POR APARTAMENTOS (3 cards)
        metrics_section = ttk.LabelFrame(self, text="📊 Resumen por Apartamentos", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 12))

        metrics_frame = ttk.Frame(metrics_section)
        metrics_frame.pack(fill=tk.X)

        self.total_apartments = MetricsCard(
            metrics_frame,
            title="Apartamentos con Gastos",
            value="0",
            subtitle="Con gastos específicos",
            icon="🏠",
            color="primary"
        )
        self.total_apartments.pack(side=tk.LEFT, expand=True, padx=4)

        self.shared_expenses = MetricsCard(
            metrics_frame,
            title="Gastos Compartidos",
            value="$0.00",
            subtitle="Gastos generales",
            icon="🤝",
            color="info"
        )
        self.shared_expenses.pack(side=tk.LEFT, expand=True, padx=4)

        self.total_by_apartments = MetricsCard(
            metrics_frame,
            title="Gastos Específicos",
            value="$0.00",
            subtitle="Por apartamento",
            icon="💰",
            color="warning"
        )
        self.total_by_apartments.pack(side=tk.LEFT, expand=True, padx=4)

        # SELECTOR DE APARTAMENTO
        selector_frame = ttk.LabelFrame(self, text="🔍 Filtro por Apartamento", padding="12")
        selector_frame.pack(fill=tk.X, pady=(0, 12))

        selector_row = ttk.Frame(selector_frame)
        selector_row.pack(fill=tk.X)

        ttk.Label(selector_row, text="Apartamento:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.apartment_var = tk.StringVar(value="Todos")
        self.apartment_combo = ttk.Combobox(
            selector_row,
            textvariable=self.apartment_var,
            values=["Todos", "Gastos Generales"],
            state="readonly",
            width=20
        )
        self.apartment_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.apartment_combo.bind("<<ComboboxSelected>>", self._on_apartment_change)

        view_btn = ttk.Button(
            selector_row,
            text="👁️ Ver Gastos",
            command=self._view_apartment_expenses,
            bootstyle="primary"
        )
        view_btn.pack(side=tk.LEFT, padx=(0, 8))

        summary_btn = ttk.Button(
            selector_row,
            text="📊 Resumen",
            command=self._show_apartment_summary,
            bootstyle="info"
        )
        summary_btn.pack(side=tk.LEFT)

        # TABLA DE GASTOS
        table_frame = ttk.LabelFrame(self, text="📋 Gastos del Apartamento Seleccionado", padding="8")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Información del apartamento seleccionado
        self.apartment_info = ttk.Label(
            table_frame,
            text="Seleccione un apartamento para ver sus gastos"
        )
        self.apartment_info.pack(anchor=tk.W, pady=(0, 5))

        # Tabla de gastos
        self.table = DataTable(
            table_frame,
            columns=[
                ("date", "Fecha"),
                ("description", "Descripción"),
                ("category", "Categoría"),
                ("amount", "Monto"),
                ("distribution", "Distribución"),
                ("status", "Estado")
            ],
            on_select=self._on_select_expense,
            on_double_click=lambda data: self._show_expense_details(data)
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _load_data(self):
        """Carga todos los gastos y los organiza por apartamento."""
        try:
            all_expenses = self.expense_service.get_all()
            
            # Organizar gastos por apartamento
            self.apartments_data = {
                "Gastos Generales": [],
                "Gastos Compartidos": []
            }
            
            apartment_set = set()
            
            for expense in all_expenses:
                # Obtener información de distribución
                distribution_type = getattr(expense, 'distribution_type', 'General')
                specific_apartment = getattr(expense, 'specific_apartment', None)
                
                if distribution_type == "Por apartamento específico" and specific_apartment:
                    apartment_set.add(specific_apartment)
                    if specific_apartment not in self.apartments_data:
                        self.apartments_data[specific_apartment] = []
                    self.apartments_data[specific_apartment].append(expense)
                elif distribution_type == "Dividir entre todos":
                    self.apartments_data["Gastos Compartidos"].append(expense)
                else:
                    self.apartments_data["Gastos Generales"].append(expense)
            
            # Actualizar combo de apartamentos
            apartment_list = ["Todos", "Gastos Generales", "Gastos Compartidos"]
            apartment_list.extend(sorted(apartment_set))
            self.apartment_combo.configure(values=apartment_list)
            
            # Actualizar métricas
            self._update_metrics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")

    def _update_metrics(self):
        """Actualiza las métricas del resumen."""
        apartments_with_expenses = len([apt for apt, expenses in self.apartments_data.items() 
                                      if apt not in ["Gastos Generales", "Gastos Compartidos"] and expenses])
        
        shared_amount = sum(e.amount for e in self.apartments_data.get("Gastos Compartidos", []))
        specific_amount = sum(
            sum(e.amount for e in expenses)
            for apt, expenses in self.apartments_data.items()
            if apt not in ["Gastos Generales", "Gastos Compartidos"]
        )
        
        self.total_apartments.update_value(str(apartments_with_expenses))
        self.shared_expenses.update_value(f"${shared_amount:,.2f}")
        self.total_by_apartments.update_value(f"${specific_amount:,.2f}")

    def _on_apartment_change(self, event=None):
        """Maneja el cambio de apartamento seleccionado."""
        self._view_apartment_expenses()

    def _view_apartment_expenses(self):
        """Muestra los gastos del apartamento seleccionado."""
        apartment = self.apartment_var.get()
        
        if apartment == "Todos":
            # Mostrar todos los gastos
            all_expenses = []
            for expenses_list in self.apartments_data.values():
                all_expenses.extend(expenses_list)
            self._update_table(all_expenses, "Todos los apartamentos")
        else:
            # Mostrar gastos del apartamento específico
            expenses = self.apartments_data.get(apartment, [])
            self._update_table(expenses, apartment)

    def _update_table(self, expenses: List[Expense], apartment_name: str):
        """Actualiza la tabla con los gastos del apartamento."""
        data = []
        total_amount = Decimal("0")
        
        for expense in expenses:
            distribution_type = getattr(expense, 'distribution_type', 'General')
            specific_apartment = getattr(expense, 'specific_apartment', None)
            
            # Determinar texto de distribución
            if distribution_type == "Por apartamento específico" and specific_apartment:
                distribution_text = f"Específico: {specific_apartment}"
            elif distribution_type == "Dividir entre todos":
                distribution_text = "Compartido entre todos"
            else:
                distribution_text = "General del edificio"
            
            data.append({
                "id": expense.id,
                "date": expense.date.strftime("%d/%m/%Y") if expense.date else "",
                "description": expense.description or "",
                "category": expense.category,
                "amount": f"${expense.amount:,.2f}",
                "distribution": distribution_text,
                "status": expense.status
            })
            
            total_amount += expense.amount
        
        self.table.set_data(data)
        self.apartment_info.configure(
            text=f"{apartment_name}: {len(data)} gasto(s) - Total: ${total_amount:,.2f}"
        )

    def _on_select_expense(self, data: Dict[str, Any]):
        """Maneja la selección de un gasto."""
        self.current_expense = data

    def _show_expense_details(self, data: Dict[str, Any]):
        """Muestra los detalles del gasto seleccionado."""
        if data and "id" in data:
            expense = self.expense_service.get_by_id(int(data["id"]))
            if expense:
                distribution_type = getattr(expense, 'distribution_type', 'General')
                specific_apartment = getattr(expense, 'specific_apartment', None)
                
                details = f"""
DETALLES DEL GASTO

Descripción: {expense.description}
Fecha: {expense.date.strftime('%d/%m/%Y')}
Monto: ${expense.amount:,.2f}
Categoría: {expense.category}
Estado: {expense.status}
Proveedor: {expense.provider or 'No especificado'}
N° Factura: {expense.invoice_number or 'No especificado'}

DISTRIBUCIÓN:
Tipo: {distribution_type}
{f'Apartamento específico: {specific_apartment}' if specific_apartment else ''}
"""
                messagebox.showinfo("Detalles del Gasto", details)

    def _show_apartment_summary(self):
        """Muestra un resumen completo por apartamentos."""
        apartment = self.apartment_var.get()
        
        if apartment == "Todos":
            # Resumen global
            summary_text = "RESUMEN GLOBAL POR APARTAMENTOS\n" + "="*50 + "\n\n"
            
            for apt_name, expenses in self.apartments_data.items():
                if expenses:  # Solo mostrar apartamentos con gastos
                    total_amount = sum(e.amount for e in expenses)
                    summary_text += f"{apt_name}:\n"
                    summary_text += f"  • {len(expenses)} gasto(s)\n"
                    summary_text += f"  • Total: ${total_amount:,.2f}\n\n"
        else:
            # Resumen específico del apartamento
            expenses = self.apartments_data.get(apartment, [])
            
            if not expenses:
                messagebox.showinfo("Sin datos", f"No hay gastos registrados para {apartment}")
                return
            
            # Agrupar por categoría
            categories = {}
            for expense in expenses:
                category = expense.category
                if category not in categories:
                    categories[category] = {'count': 0, 'total': Decimal('0')}
                categories[category]['count'] += 1
                categories[category]['total'] += expense.amount
            
            total_amount = sum(e.amount for e in expenses)
            
            summary_text = f"RESUMEN DETALLADO - {apartment.upper()}\n" + "="*50 + "\n\n"
            summary_text += f"Total de gastos: {len(expenses)}\n"
            summary_text += f"Monto total: ${total_amount:,.2f}\n\n"
            summary_text += "POR CATEGORÍAS:\n" + "-"*20 + "\n"
            
            for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
                percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
                summary_text += f"{category}: ${data['total']:,.2f} ({percentage:.1f}%) - {data['count']} gasto(s)\n"
        
        # Mostrar ventana de resumen
        summary_window = tk.Toplevel(self)
        summary_window.title(f"Resumen - {apartment}")
        summary_window.geometry("500x400")
        summary_window.transient(self)
        
        text_widget = tk.Text(summary_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, summary_text)
        text_widget.configure(state=tk.DISABLED)

    def _go_back_to_expenses_dashboard(self):
        """Vuelve al dashboard de gastos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_dashboard')

    def refresh(self):
        """Actualiza la vista."""
        self._load_data() 