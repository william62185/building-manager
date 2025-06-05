import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, date, timedelta
import csv
import calendar

from ...models.expense import Expense
from ...services.expense_service import ExpenseService
from ..components import DataTable, MetricsCard


class ExpensesAnalyticsView(ttk.Frame):
    """Vista de análisis avanzado de gastos con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.expense_service = ExpenseService()
        self.current_expenses: List[Expense] = []
        self.analysis_period = "Último año"
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz de análisis de gastos."""
        self.configure(padding="12")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="📊 Análisis de Gastos",
            font=("Segoe UI", 18, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Análisis detallado por categorías y tendencias",
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

        # RESUMEN ANALÍTICO (4 cards horizontales)
        metrics_section = ttk.LabelFrame(self, text="📈 Resumen Analítico", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 12))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas analíticas
        self.total_analyzed = MetricsCard(
            all_metrics,
            title="Total Analizado",
            value="$0.00",
            subtitle="Período seleccionado",
            icon="📊",
            color="primary"
        )
        self.total_analyzed.pack(side=tk.LEFT, expand=True, padx=2)

        self.category_count = MetricsCard(
            all_metrics,
            title="Categorías Activas",
            value="0",
            subtitle="Con gastos registrados",
            icon="📋",
            color="info"
        )
        self.category_count.pack(side=tk.LEFT, expand=True, padx=2)

        self.monthly_average = MetricsCard(
            all_metrics,
            title="Promedio Mensual",
            value="$0.00",
            subtitle="Gasto promedio/mes",
            icon="📅",
            color="warning"
        )
        self.monthly_average.pack(side=tk.LEFT, expand=True, padx=2)

        self.trend_indicator = MetricsCard(
            all_metrics,
            title="Tendencia",
            value="Estable",
            subtitle="Comparativa temporal",
            icon="📈",
            color="success"
        )
        self.trend_indicator.pack(side=tk.LEFT, expand=True, padx=2)

        # FILTROS DE ANÁLISIS
        filters_frame = ttk.LabelFrame(self, text="🔧 Configuración de Análisis", padding="12")
        filters_frame.pack(fill=tk.X, pady=(0, 12))

        # Primera fila: período y tipo de análisis
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
                "Últimos 2 años",
                "Todo el historial"
            ],
            state="readonly",
            width=15
        )
        period_combo.pack(side=tk.LEFT, padx=(0, 15))
        period_combo.bind("<<ComboboxSelected>>", self._on_period_change)

        ttk.Label(filter_row1, text="Análisis por:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.analysis_type = tk.StringVar(value="Categorías")
        analysis_combo = ttk.Combobox(
            filter_row1,
            textvariable=self.analysis_type,
            values=["Categorías", "Proveedores", "Meses", "Gastos Recurrentes"],
            state="readonly",
            width=15
        )
        analysis_combo.pack(side=tk.LEFT, padx=(0, 15))
        analysis_combo.bind("<<ComboboxSelected>>", self._on_analysis_change)

        # Botón de análisis
        analyze_btn = ttk.Button(
            filter_row1,
            text="📊 Analizar",
            command=self._perform_analysis,
            bootstyle="primary"
        )
        analyze_btn.pack(side=tk.LEFT)

        # HERRAMIENTAS DE ANÁLISIS
        tools_frame = ttk.Frame(filters_frame)
        tools_frame.pack(fill=tk.X)

        # Botones de herramientas
        compare_btn = ttk.Button(
            tools_frame,
            text="📈 Comparar Períodos",
            command=self._compare_periods,
            bootstyle="info"
        )
        compare_btn.pack(side=tk.LEFT, padx=(0, 8))

        forecast_btn = ttk.Button(
            tools_frame,
            text="🔮 Proyección",
            command=self._forecast_expenses,
            bootstyle="success"
        )
        forecast_btn.pack(side=tk.LEFT, padx=(0, 8))

        budget_btn = ttk.Button(
            tools_frame,
            text="💰 Análisis de Presupuesto",
            command=self._budget_analysis,
            bootstyle="warning"
        )
        budget_btn.pack(side=tk.LEFT, padx=(0, 8))

        export_analysis_btn = ttk.Button(
            tools_frame,
            text="📤 Exportar Análisis",
            command=self._export_analysis,
            bootstyle="outline-primary"
        )
        export_analysis_btn.pack(side=tk.RIGHT)

        # RESULTADOS DEL ANÁLISIS
        results_frame = ttk.LabelFrame(self, text="📋 Resultados del Análisis", padding="8")
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Información del análisis actual
        self.analysis_info = ttk.Label(
            results_frame, 
            text=f"Análisis por {self.analysis_type.get()} - {self.period_filter.get()}"
        )
        self.analysis_info.pack(anchor=tk.W, pady=(0, 5))

        # Tabla de análisis
        self.analysis_table = DataTable(
            results_frame,
            columns=[
                ("category", "Categoría/Item"),
                ("total_amount", "Monto Total"),
                ("percentage", "% del Total"),
                ("count", "Cantidad"),
                ("average", "Promedio"),
                ("trend", "Tendencia")
            ],
            on_select=self._on_select_analysis_item,
            on_double_click=lambda data: self._show_detailed_analysis(data)
        )
        self.analysis_table.pack(fill=tk.BOTH, expand=True)

        # PANEL DE DETALLES DEL ANÁLISIS
        details_frame = ttk.LabelFrame(self, text="ℹ️ Detalles del Análisis", padding="12")
        details_frame.pack(fill=tk.X, pady=(12, 0))

        self.details_text = tk.Text(
            details_frame,
            height=5,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.X)

    def _load_data(self):
        """Carga todos los gastos para análisis."""
        try:
            self.current_expenses = self.expense_service.get_all()
            self._perform_analysis()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos para análisis: {e}")

    def _on_period_change(self, event=None):
        """Maneja cambios en el período de análisis."""
        self._perform_analysis()

    def _on_analysis_change(self, event=None):
        """Maneja cambios en el tipo de análisis."""
        self._perform_analysis()

    def _perform_analysis(self):
        """Realiza el análisis según los criterios seleccionados."""
        try:
            period = self.period_filter.get()
            analysis_type = self.analysis_type.get()
            
            # Filtrar gastos por período
            filtered_expenses = self._filter_by_period(period)
            
            # Realizar análisis según el tipo
            if analysis_type == "Categorías":
                analysis_data = self._analyze_by_categories(filtered_expenses)
            elif analysis_type == "Proveedores":
                analysis_data = self._analyze_by_providers(filtered_expenses)
            elif analysis_type == "Meses":
                analysis_data = self._analyze_by_months(filtered_expenses)
            elif analysis_type == "Gastos Recurrentes":
                analysis_data = self._analyze_recurring_expenses(filtered_expenses)
            else:
                analysis_data = []

            # Actualizar tabla y métricas
            self._update_analysis_table(analysis_data)
            self._update_analysis_metrics(filtered_expenses, analysis_data)
            
            # Actualizar información del análisis
            self.analysis_info.configure(
                text=f"Análisis por {analysis_type} - {period} ({len(filtered_expenses)} gastos)"
            )
            
        except Exception as e:
            print(f"Error en análisis: {e}")
            messagebox.showerror("Error", f"Error al realizar análisis: {e}")

    def _filter_by_period(self, period):
        """Filtra gastos por el período seleccionado."""
        today = date.today()
        
        if period == "Último mes":
            start_date = today.replace(day=1)
        elif period == "Últimos 3 meses":
            start_date = today - timedelta(days=90)
        elif period == "Últimos 6 meses":
            start_date = today - timedelta(days=180)
        elif period == "Último año":
            start_date = today - timedelta(days=365)
        elif period == "Últimos 2 años":
            start_date = today - timedelta(days=730)
        else:  # Todo el historial
            return self.current_expenses
        
        return [e for e in self.current_expenses if e.date >= start_date]

    def _analyze_by_categories(self, expenses):
        """Analiza gastos por categorías."""
        category_data = {}
        total_amount = sum(e.amount for e in expenses)
        
        for expense in expenses:
            category = expense.category
            if category not in category_data:
                category_data[category] = {
                    'total': Decimal('0'),
                    'count': 0,
                    'expenses': []
                }
            
            category_data[category]['total'] += expense.amount
            category_data[category]['count'] += 1
            category_data[category]['expenses'].append(expense)
        
        # Convertir a lista ordenada
        analysis_data = []
        for category, data in sorted(category_data.items(), key=lambda x: x[1]['total'], reverse=True):
            percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
            average = data['total'] / data['count'] if data['count'] > 0 else Decimal('0')
            
            analysis_data.append({
                'category': category,
                'total_amount': f"${data['total']:,.2f}",
                'percentage': f"{percentage:.1f}%",
                'count': str(data['count']),
                'average': f"${average:,.2f}",
                'trend': self._calculate_trend(data['expenses'])
            })
        
        return analysis_data

    def _analyze_by_providers(self, expenses):
        """Analiza gastos por proveedores."""
        provider_data = {}
        total_amount = sum(e.amount for e in expenses)
        
        for expense in expenses:
            provider = expense.provider or "Sin proveedor"
            if provider not in provider_data:
                provider_data[provider] = {
                    'total': Decimal('0'),
                    'count': 0,
                    'expenses': []
                }
            
            provider_data[provider]['total'] += expense.amount
            provider_data[provider]['count'] += 1
            provider_data[provider]['expenses'].append(expense)
        
        # Convertir a lista ordenada
        analysis_data = []
        for provider, data in sorted(provider_data.items(), key=lambda x: x[1]['total'], reverse=True):
            percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
            average = data['total'] / data['count'] if data['count'] > 0 else Decimal('0')
            
            analysis_data.append({
                'category': provider,
                'total_amount': f"${data['total']:,.2f}",
                'percentage': f"{percentage:.1f}%",
                'count': str(data['count']),
                'average': f"${average:,.2f}",
                'trend': self._calculate_trend(data['expenses'])
            })
        
        return analysis_data

    def _analyze_by_months(self, expenses):
        """Analiza gastos por meses."""
        month_data = {}
        
        for expense in expenses:
            month_key = expense.date.strftime("%Y-%m")
            month_name = expense.date.strftime("%B %Y")
            
            if month_key not in month_data:
                month_data[month_key] = {
                    'name': month_name,
                    'total': Decimal('0'),
                    'count': 0,
                    'expenses': []
                }
            
            month_data[month_key]['total'] += expense.amount
            month_data[month_key]['count'] += 1
            month_data[month_key]['expenses'].append(expense)
        
        # Convertir a lista ordenada por fecha
        analysis_data = []
        total_amount = sum(data['total'] for data in month_data.values())
        
        for month_key, data in sorted(month_data.items(), reverse=True):
            percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
            average = data['total'] / data['count'] if data['count'] > 0 else Decimal('0')
            
            analysis_data.append({
                'category': data['name'],
                'total_amount': f"${data['total']:,.2f}",
                'percentage': f"{percentage:.1f}%",
                'count': str(data['count']),
                'average': f"${average:,.2f}",
                'trend': "📊 Mensual"
            })
        
        return analysis_data

    def _analyze_recurring_expenses(self, expenses):
        """Analiza gastos recurrentes."""
        recurring_expenses = [e for e in expenses if getattr(e, 'is_recurring', False)]
        
        # Agrupar por descripción similar
        recurring_data = {}
        for expense in recurring_expenses:
            key = expense.description
            if key not in recurring_data:
                recurring_data[key] = {
                    'total': Decimal('0'),
                    'count': 0,
                    'expenses': []
                }
            
            recurring_data[key]['total'] += expense.amount
            recurring_data[key]['count'] += 1
            recurring_data[key]['expenses'].append(expense)
        
        # Convertir a lista
        analysis_data = []
        total_amount = sum(data['total'] for data in recurring_data.values())
        
        for description, data in sorted(recurring_data.items(), key=lambda x: x[1]['total'], reverse=True):
            percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
            average = data['total'] / data['count'] if data['count'] > 0 else Decimal('0')
            
            analysis_data.append({
                'category': description,
                'total_amount': f"${data['total']:,.2f}",
                'percentage': f"{percentage:.1f}%",
                'count': str(data['count']),
                'average': f"${average:,.2f}",
                'trend': "🔄 Recurrente"
            })
        
        return analysis_data

    def _calculate_trend(self, expenses):
        """Calcula la tendencia de una serie de gastos."""
        if len(expenses) < 2:
            return "📊 Nuevo"
        
        # Ordenar por fecha
        sorted_expenses = sorted(expenses, key=lambda x: x.date)
        
        # Comparar primera y segunda mitad
        mid_point = len(sorted_expenses) // 2
        first_half = sorted_expenses[:mid_point]
        second_half = sorted_expenses[mid_point:]
        
        first_avg = sum(e.amount for e in first_half) / len(first_half)
        second_avg = sum(e.amount for e in second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "📈 Creciente"
        elif second_avg < first_avg * 0.9:
            return "📉 Decreciente"
        else:
            return "📊 Estable"

    def _update_analysis_table(self, analysis_data):
        """Actualiza la tabla de análisis."""
        self.analysis_table.set_data(analysis_data)

    def _update_analysis_metrics(self, expenses, analysis_data):
        """Actualiza las métricas del análisis."""
        if not expenses:
            self.total_analyzed.update_value("$0.00")
            self.category_count.update_value("0")
            self.monthly_average.update_value("$0.00")
            self.trend_indicator.update_value("Sin datos")
            return
        
        total_amount = sum(e.amount for e in expenses)
        category_count = len(analysis_data)
        
        # Calcular promedio mensual
        if len(expenses) > 0:
            first_date = min(e.date for e in expenses)
            last_date = max(e.date for e in expenses)
            months_diff = max(1, (last_date.year - first_date.year) * 12 + last_date.month - first_date.month + 1)
            monthly_avg = total_amount / months_diff
        else:
            monthly_avg = Decimal('0')
        
        # Actualizar métricas
        self.total_analyzed.update_value(f"${total_amount:,.2f}")
        self.category_count.update_value(str(category_count))
        self.monthly_average.update_value(f"${monthly_avg:,.2f}")
        
        # Calcular tendencia general
        overall_trend = self._calculate_trend(expenses)
        self.trend_indicator.update_value(overall_trend)

    def _on_select_analysis_item(self, data: Dict[str, Any]):
        """Maneja la selección de un item de análisis."""
        if data:
            details = f"Análisis seleccionado: {data.get('category', 'N/A')}\n"
            details += f"Monto total: {data.get('total_amount', 'N/A')}\n"
            details += f"Porcentaje del total: {data.get('percentage', 'N/A')}\n"
            details += f"Cantidad de gastos: {data.get('count', 'N/A')}\n"
            details += f"Promedio por gasto: {data.get('average', 'N/A')}\n"
            details += f"Tendencia: {data.get('trend', 'N/A')}"
            
            self._update_details_panel(details)

    def _update_details_panel(self, details):
        """Actualiza el panel de detalles."""
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.configure(state=tk.DISABLED)

    def _show_detailed_analysis(self, data: Dict[str, Any]):
        """Muestra análisis detallado del item seleccionado."""
        category = data.get('category', 'Item')
        
        # Crear ventana de análisis detallado
        detail_window = tk.Toplevel(self)
        detail_window.title(f"Análisis Detallado - {category}")
        detail_window.geometry("600x400")
        detail_window.transient(self)
        
        # Contenido del análisis detallado
        text_widget = tk.Text(detail_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        details = f"ANÁLISIS DETALLADO - {category.upper()}\n"
        details += "="*50 + "\n\n"
        details += f"Total gastado: {data.get('total_amount', 'N/A')}\n"
        details += f"Porcentaje del total: {data.get('percentage', 'N/A')}\n"
        details += f"Número de gastos: {data.get('count', 'N/A')}\n"
        details += f"Promedio por gasto: {data.get('average', 'N/A')}\n"
        details += f"Tendencia observada: {data.get('trend', 'N/A')}\n\n"
        details += "RECOMENDACIONES:\n"
        details += "- Revise los gastos más altos de esta categoría\n"
        details += "- Compare con períodos anteriores\n"
        details += "- Evalúe oportunidades de optimización\n"
        
        text_widget.insert(tk.END, details)
        text_widget.configure(state=tk.DISABLED)

    def _compare_periods(self):
        """Compara gastos entre diferentes períodos."""
        messagebox.showinfo(
            "Comparación de Períodos",
            "Función de comparación de períodos en desarrollo.\n\n" +
            "Esta función permitirá comparar:\n" +
            "• Gastos mes a mes\n" +
            "• Tendencias anuales\n" +
            "• Variaciones estacionales\n" +
            "• Análisis de crecimiento"
        )

    def _forecast_expenses(self):
        """Genera proyecciones de gastos."""
        messagebox.showinfo(
            "Proyección de Gastos",
            "Función de proyección en desarrollo.\n\n" +
            "Esta función incluirá:\n" +
            "• Proyección basada en tendencias\n" +
            "• Estimados por categoría\n" +
            "• Presupuesto recomendado\n" +
            "• Alertas de sobrecostos"
        )

    def _budget_analysis(self):
        """Realiza análisis de presupuesto."""
        messagebox.showinfo(
            "Análisis de Presupuesto",
            "Función de análisis de presupuesto en desarrollo.\n\n" +
            "Esta función permitirá:\n" +
            "• Definir presupuestos por categoría\n" +
            "• Comparar gasto real vs presupuesto\n" +
            "• Alertas de sobregasto\n" +
            "• Recomendaciones de optimización"
        )

    def _export_analysis(self):
        """Exporta el análisis actual."""
        if not self.analysis_table.get_data():
            messagebox.showwarning("Advertencia", "No hay análisis para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Exportar análisis de gastos"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = ["Categoría/Item", "Monto Total", "% del Total", "Cantidad", "Promedio", "Tendencia"]
                    writer.writerow(headers)
                    
                    # Escribir datos del análisis
                    for row in self.analysis_table.get_data():
                        csv_row = [
                            row.get('category', ''),
                            row.get('total_amount', ''),
                            row.get('percentage', ''),
                            row.get('count', ''),
                            row.get('average', ''),
                            row.get('trend', '')
                        ]
                        writer.writerow(csv_row)
                
                messagebox.showinfo("Éxito", f"Análisis exportado correctamente a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar análisis: {e}")

    def _go_back_to_expenses_dashboard(self):
        """Vuelve al dashboard de gastos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_dashboard')

    def refresh(self):
        """Actualiza la vista."""
        self._load_data() 