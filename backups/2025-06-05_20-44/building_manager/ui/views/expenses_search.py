import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date
import csv

from ...models.expense import Expense
from ...services.expense_service import ExpenseService
from ..components import DataTable, MetricsCard


class ExpensesSearchView(ttk.Frame):
    """Vista de búsqueda avanzada de gastos con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.expense_service = ExpenseService()
        self.filtered_expenses: List[Expense] = []
        self.current_expense: Optional[Expense] = None
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de búsqueda de gastos."""
        self.configure(padding="12")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="🔍 Búsqueda de Gastos",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Búsqueda avanzada y análisis de gastos",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        subtitle.pack()
        
        # Botones de navegación
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        back_btn = ttk.Button(
            nav_frame,
            text="← Dashboard Gastos",
            command=self._go_back_to_expenses_dashboard,
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
            title="Gastos Encontrados",
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
            subtitle="Suma de gastos",
            icon="💰",
            color="danger"
        )
        self.total_amount.pack(side=tk.LEFT, expand=True, padx=2)

        self.by_category = MetricsCard(
            all_metrics,
            title="Categoría Principal",
            value="N/A",
            subtitle="Mayor gasto",
            icon="📊",
            color="warning"
        )
        self.by_category.pack(side=tk.LEFT, expand=True, padx=2)

        self.pending_expenses = MetricsCard(
            all_metrics,
            title="Gastos Pendientes",
            value="0",
            subtitle="Sin pagar",
            icon="⏰",
            color="info"
        )
        self.pending_expenses.pack(side=tk.LEFT, expand=True, padx=2)

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
        
        ttk.Label(search_row1, text="(Descripción, proveedor, monto...)", 
                 bootstyle="secondary").pack(side=tk.LEFT, padx=(0, 10))

        clear_btn = ttk.Button(
            search_row1,
            text="🗑️ Limpiar",
            command=self._clear_search,
            bootstyle="outline-secondary"
        )
        clear_btn.pack(side=tk.LEFT)

        # Segunda fila: filtros principales
        search_row2 = ttk.Frame(search_frame)
        search_row2.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_row2, text="Categoría:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.category_filter = tk.StringVar(value="Todas")
        category_combo = ttk.Combobox(
            search_row2,
            textvariable=self.category_filter,
            values=[
                "Todas", "Mantenimiento", "Servicios", "Reparaciones",
                "Impuestos", "Seguros", "Limpieza", "Otro"
            ],
            state="readonly",
            width=15
        )
        category_combo.pack(side=tk.LEFT, padx=(0, 15))
        category_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(search_row2, text="Estado:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(
            search_row2,
            textvariable=self.status_filter,
            values=["Todos", "Pagado", "Pendiente", "Anulado"],
            state="readonly",
            width=12
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(search_row2, text="Ordenar por:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="Fecha (Desc)")
        sort_combo = ttk.Combobox(
            search_row2,
            textvariable=self.sort_var,
            values=["Fecha (Desc)", "Fecha (Asc)", "Monto (Desc)", "Monto (Asc)", "Categoría", "Proveedor"],
            state="readonly",
            width=15
        )
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Tercera fila: filtros por fechas y montos
        search_row3 = ttk.Frame(search_frame)
        search_row3.pack(fill=tk.X)

        ttk.Label(search_row3, text="Desde:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_date = tk.StringVar()
        start_entry = ttk.Entry(search_row3, textvariable=self.start_date, width=12)
        start_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(search_row3, text="Hasta:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.end_date = tk.StringVar()
        end_entry = ttk.Entry(search_row3, textvariable=self.end_date, width=12)
        end_entry.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(search_row3, text="Monto min:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.min_amount = tk.StringVar()
        min_entry = ttk.Entry(search_row3, textvariable=self.min_amount, width=10)
        min_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(search_row3, text="Monto max:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.max_amount = tk.StringVar()
        max_entry = ttk.Entry(search_row3, textvariable=self.max_amount, width=10)
        max_entry.pack(side=tk.LEFT, padx=(0, 15))

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

        category_report_btn = ttk.Button(
            actions_left,
            text="📊 Reporte por Categorías",
            command=self._category_report,
            bootstyle="info"
        )
        category_report_btn.pack(side=tk.LEFT, padx=(0, 8))

        refresh_btn = ttk.Button(
            actions_left,
            text="🔄 Actualizar",
            command=self._refresh_data,
            bootstyle="outline-primary"
        )
        refresh_btn.pack(side=tk.LEFT)

        # TABLA DE RESULTADOS
        table_frame = ttk.LabelFrame(self, text="📋 Resultados de Búsqueda", padding="8")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Contador de registros
        self.records_label = ttk.Label(table_frame, text="0 gastos encontrados")
        self.records_label.pack(anchor=tk.W, pady=(0, 5))

        # Tabla de gastos
        self.table = DataTable(
            table_frame,
            columns=[
                ("date", "Fecha"),
                ("description", "Descripción"),
                ("category", "Categoría"),
                ("amount", "Monto"),
                ("provider", "Proveedor"),
                ("status", "Estado"),
                ("invoice_number", "N° Factura")
            ],
            on_select=self._on_select_expense,
            on_double_click=lambda data: self._show_expense_details(data)
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _load_data(self):
        """Carga todos los gastos."""
        try:
            expenses = self.expense_service.get_all()
            self.filtered_expenses = expenses
            self._update_table()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar gastos: {e}")

    def _update_table(self):
        """Actualiza la tabla con los gastos filtrados."""
        data = []
        total_amount = Decimal("0")
        pending_count = 0
        category_totals = {}
        
        for expense in self.filtered_expenses:
            data.append({
                "id": expense.id,
                "date": expense.date.strftime("%d/%m/%Y") if expense.date else "",
                "description": expense.description or "",
                "category": expense.category,
                "amount": f"${expense.amount:,.2f}",
                "provider": expense.provider or "N/A",
                "status": expense.status,
                "invoice_number": expense.invoice_number or "N/A"
            })
            
            # Calcular estadísticas
            total_amount += expense.amount
            if expense.status == "Pendiente":
                pending_count += 1
            
            # Agrupar por categoría
            if expense.category in category_totals:
                category_totals[expense.category] += expense.amount
            else:
                category_totals[expense.category] = expense.amount
        
        self.table.set_data(data)
        self.records_label.configure(text=f"{len(data)} gasto(s) encontrado(s)")
        
        # Encontrar categoría principal
        main_category = "N/A"
        if category_totals:
            main_category = max(category_totals, key=category_totals.get)
        
        # Actualizar métricas
        self.total_found.update_value(str(len(data)))
        self.total_amount.update_value(f"${total_amount:,.2f}")
        self.by_category.update_value(main_category)
        self.pending_expenses.update_value(str(pending_count))

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
            category_filter = self.category_filter.get()
            status_filter = self.status_filter.get()
            sort_by = self.sort_var.get()
            start_date_str = self.start_date.get().strip()
            end_date_str = self.end_date.get().strip()
            min_amount_str = self.min_amount.get().strip()
            max_amount_str = self.max_amount.get().strip()

            # Obtener todos los gastos
            all_expenses = self.expense_service.get_all()
            
            # Aplicar filtro de categoría
            if category_filter != "Todas":
                all_expenses = [e for e in all_expenses if e.category == category_filter]
            
            # Aplicar filtro de estado
            if status_filter != "Todos":
                all_expenses = [e for e in all_expenses if e.status == status_filter]
            
            # Aplicar filtro de fechas
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()
                    all_expenses = [e for e in all_expenses if e.date >= start_date]
                except ValueError:
                    pass
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()
                    all_expenses = [e for e in all_expenses if e.date <= end_date]
                except ValueError:
                    pass

            # Aplicar filtro de montos
            if min_amount_str:
                try:
                    min_amount = Decimal(min_amount_str)
                    all_expenses = [e for e in all_expenses if e.amount >= min_amount]
                except ValueError:
                    pass

            if max_amount_str:
                try:
                    max_amount = Decimal(max_amount_str)
                    all_expenses = [e for e in all_expenses if e.amount <= max_amount]
                except ValueError:
                    pass
            
            # Aplicar búsqueda de texto
            if search_text:
                filtered = []
                for expense in all_expenses:
                    # Buscar en descripción, proveedor, monto, número de factura
                    if (search_text in expense.description.lower() if expense.description else False or
                        search_text in (expense.provider or "").lower() or
                        search_text in str(expense.amount) or
                        search_text in (expense.invoice_number or "").lower()):
                        filtered.append(expense)
                all_expenses = filtered
            
            # Aplicar ordenamiento
            if sort_by == "Fecha (Desc)":
                all_expenses.sort(key=lambda e: e.date, reverse=True)
            elif sort_by == "Fecha (Asc)":
                all_expenses.sort(key=lambda e: e.date)
            elif sort_by == "Monto (Desc)":
                all_expenses.sort(key=lambda e: e.amount, reverse=True)
            elif sort_by == "Monto (Asc)":
                all_expenses.sort(key=lambda e: e.amount)
            elif sort_by == "Categoría":
                all_expenses.sort(key=lambda e: e.category)
            elif sort_by == "Proveedor":
                all_expenses.sort(key=lambda e: e.provider or "")

            self.filtered_expenses = all_expenses
            self._update_table()
            
        except Exception as e:
            print(f"Error al aplicar filtros: {e}")
            messagebox.showerror("Error", f"Error al filtrar datos: {e}")

    def _clear_search(self):
        """Limpia la búsqueda y filtros."""
        self.search_var.set("")
        self.category_filter.set("Todas")
        self.status_filter.set("Todos")
        self.sort_var.set("Fecha (Desc)")
        self.start_date.set("")
        self.end_date.set("")
        self.min_amount.set("")
        self.max_amount.set("")
        self._apply_filters()

    def _on_select_expense(self, data: Dict[str, Any]):
        """Maneja la selección de un gasto."""
        if data and "id" in data:
            self.current_expense = self.expense_service.get_by_id(int(data["id"]))
        else:
            self.current_expense = None

    def _show_expense_details(self, data: Dict[str, Any]):
        """Muestra los detalles del gasto seleccionado."""
        if data and "id" in data:
            expense = self.expense_service.get_by_id(int(data["id"]))
            if expense:
                details = f"""
DETALLES DEL GASTO

Descripción: {expense.description}
Fecha: {expense.date.strftime('%d/%m/%Y')}
Monto: ${expense.amount:,.2f}
Categoría: {expense.category}
Estado: {expense.status}
Proveedor: {expense.provider or 'No especificado'}
N° Factura: {expense.invoice_number or 'No especificado'}
Método de Pago: {getattr(expense, 'payment_method', 'No especificado')}
Recurrente: {'Sí' if getattr(expense, 'is_recurring', False) else 'No'}
"""
                messagebox.showinfo("Detalles del Gasto", details)

    def _export_data(self):
        """Exporta los datos actuales a CSV."""
        if not self.filtered_expenses:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar datos de gastos"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = ["Fecha", "Descripción", "Categoría", "Monto", "Proveedor", "Estado", "N° Factura"]
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for expense in self.filtered_expenses:
                        row = [
                            expense.date.strftime("%d/%m/%Y"),
                            expense.description,
                            expense.category,
                            f"${expense.amount:,.2f}",
                            expense.provider or "",
                            expense.status,
                            expense.invoice_number or ""
                        ]
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar datos: {e}")

    def _category_report(self):
        """Genera un reporte por categorías."""
        if not self.filtered_expenses:
            messagebox.showwarning("Advertencia", "No hay datos para el reporte.")
            return

        # Calcular totales por categoría
        category_totals = {}
        for expense in self.filtered_expenses:
            if expense.category in category_totals:
                category_totals[expense.category] += expense.amount
            else:
                category_totals[expense.category] = expense.amount

        # Mostrar reporte
        report = "REPORTE POR CATEGORÍAS\n" + "="*40 + "\n\n"
        for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            report += f"{category}: ${total:,.2f}\n"
        
        # Crear ventana para mostrar el reporte
        report_window = tk.Toplevel(self)
        report_window.title("Reporte por Categorías")
        report_window.geometry("400x300")
        report_window.transient(self)
        
        text_widget = tk.Text(report_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, report)
        text_widget.configure(state=tk.DISABLED)

    def _refresh_data(self):
        """Actualiza los datos de la tabla."""
        self._load_data()

    def _go_back_to_expenses_dashboard(self):
        """Vuelve al dashboard de gastos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_dashboard')

    def refresh(self):
        """Actualiza la vista."""
        self._refresh_data() 