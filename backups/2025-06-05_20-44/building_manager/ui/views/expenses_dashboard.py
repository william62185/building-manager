import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from typing import Any, Dict, List, Optional
from datetime import date, timedelta
from decimal import Decimal

from ...services.expense_service import ExpenseService
from ..components import MetricsCard


class ExpensesDashboard(ttk.Frame):
    """Dashboard específico para la gestión de gastos con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.expense_service = ExpenseService()
        
        # Variable para el modo oscuro
        self.dark_mode = False
        
        # Lista para almacenar referencias de botones para actualización dinámica
        self.module_buttons = []
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz del dashboard de gastos."""
        # Contenedor principal OPTIMIZADO PARA PANTALLA COMPLETA
        self.configure(padding="4")

        # HEADER CON TÍTULO Y NAVEGACIÓN
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Título principal
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        main_title = ttk.Label(
            title_frame,
            text="📊 Dashboard de Gastos",
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary"
        )
        main_title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Control integral de gastos y análisis de costos",
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        subtitle.pack()
        
        # Botón de retorno al dashboard principal
        back_btn = ttk.Button(
            header_frame,
            text="← Volver al Dashboard",
            command=self._go_back_to_main,
            bootstyle="outline-secondary"
        )
        back_btn.pack(side=tk.RIGHT)

        # RESUMEN DE GASTOS (4 cards horizontales)
        metrics_section = ttk.LabelFrame(self, text="📈 Resumen de Gastos del Mes", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 6))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas de gastos - ESPACIADO REDUCIDO
        self.monthly_total = MetricsCard(
            all_metrics,
            title="Gastos del Mes",
            value="$0.00",
            subtitle="Total ejecutado",
            icon="💸",
            color="danger"
        )
        self.monthly_total.pack(side=tk.LEFT, expand=True, padx=2)

        self.total_expenses = MetricsCard(
            all_metrics,
            title="Número de Gastos",
            value="0",
            subtitle="Gastos registrados",
            icon="📋",
            color="primary"
        )
        self.total_expenses.pack(side=tk.LEFT, expand=True, padx=2)

        self.pending_expenses = MetricsCard(
            all_metrics,
            title="Gastos Pendientes",
            value="0",
            subtitle="Por pagar",
            icon="⏰",
            color="warning"
        )
        self.pending_expenses.pack(side=tk.LEFT, expand=True, padx=2)

        self.average_expense = MetricsCard(
            all_metrics,
            title="Promedio por Gasto",
            value="$0.00",
            subtitle="Gasto promedio",
            icon="📊",
            color="info"
        )
        self.average_expense.pack(side=tk.LEFT, expand=True, padx=2)

        # ACCIONES PRINCIPALES (Grid 2x3) - MUCHO MÁS GRANDES
        actions_section = ttk.LabelFrame(self, text="🚀 Acciones Principales", padding="8")
        actions_section.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

        # Primera fila de acciones principales - MUCHO MÁS GRANDES
        first_row = ttk.Frame(actions_section)
        first_row.pack(fill=tk.BOTH, expand=True, pady=(2, 4))

        # Crear botones con sombra personalizada - COLORES ESPECÍFICOS PARA GASTOS
        self._create_shadow_button(
            first_row, "💰 Registrar Nuevo Gasto\nAgregar gasto del edificio", 
            "#F44336", "white", self._register_expense, "register_expense"
        )

        self._create_shadow_button(
            first_row, "🔍 Buscar Gastos\nBúsqueda avanzada", 
            "#2196F3", "white", self._search_expenses, "search_expenses"
        )

        self._create_shadow_button(
            first_row, "📊 Análisis de Categorías\nGastos por tipología", 
            "#9C27B0", "white", self._category_analysis, "category_analysis"
        )

        # Segunda fila de acciones principales
        second_row = ttk.Frame(actions_section)
        second_row.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        self._create_shadow_button(
            second_row, "🏢 Gastos por Apartamento\nSeparación detallada", 
            "#4CAF50", "white", self._expenses_by_apartment, "expenses_by_apartment"
        )

        self._create_shadow_button(
            second_row, "📅 Gastos del Mes\nResumen mensual completo", 
            "#00BCD4", "white", self._monthly_expenses, "monthly_expenses"
        )

        self._create_shadow_button(
            second_row, "📈 Reportes Ejecutivos\nAnálisis y tendencias", 
            "#673AB7", "white", self._executive_reports, "executive_reports"
        )

    def _create_shadow_button(self, parent, text, bg_color, fg_color, command, module_id=None):
        """Crea un botón con efecto de sombra y tipografía mejorada - IDÉNTICO AL DASHBOARD."""
        # Frame contenedor para el efecto de sombra
        shadow_frame = ttk.Frame(parent)
        shadow_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=2)
        
        # Frame de sombra (fondo gris desplazado)
        shadow = tk.Frame(
            shadow_frame,
            bg="#404040",  # Color de sombra
            relief="flat"
        )
        shadow.place(x=3, y=3, relwidth=1, relheight=1)
        
        # Frame principal del botón para contener el contenido
        button_frame = tk.Frame(
            shadow_frame,
            bg=bg_color,
            relief="raised",
            bd=2,
            cursor="hand2"
        )
        button_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Separar el texto en líneas
        lines = text.split('\n')
        module_name = lines[0] if lines else text
        description = lines[1] if len(lines) > 1 else ""
        
        # Contenedor interno para centrar el contenido
        content_frame = tk.Frame(button_frame, bg=bg_color)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título del módulo (más grande)
        title_label = tk.Label(
            content_frame,
            text=module_name,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 16, "bold"),
            cursor="hand2"
        )
        title_label.pack()
        
        # Descripción (más pequeña y diferente estilo)
        desc_label = None
        if description:
            desc_label = tk.Label(
                content_frame,
                text=description,
                bg=bg_color,
                fg=fg_color,
                font=("Segoe UI", 11, "normal"),
                cursor="hand2"
            )
            desc_label.pack(pady=(2, 0))
        
        # FORZAR COLORES INMEDIATAMENTE - MISMA LÓGICA DEL DASHBOARD
        for _ in range(3):
            button_frame.configure(bg=bg_color)
            content_frame.configure(bg=bg_color)  
            title_label.configure(bg=bg_color, fg=fg_color)
            if desc_label:
                desc_label.configure(bg=bg_color, fg=fg_color)
                
        # Función para forzar colores después del renderizado
        def force_colors_delayed():
            try:
                button_frame.configure(bg=bg_color)
                content_frame.configure(bg=bg_color)
                title_label.configure(bg=bg_color, fg=fg_color)
                if desc_label:
                    desc_label.configure(bg=bg_color, fg=fg_color)
            except:
                pass
                
        # Programar aplicaciones adicionales en diferentes momentos
        self.after(10, force_colors_delayed)
        self.after(50, force_colors_delayed)
        self.after(100, force_colors_delayed)
        
        # Hacer que todos los elementos respondan al clic
        def on_button_click(event=None):
            try:
                command()
            except Exception as e:
                print(f"Error ejecutando comando del botón {module_id}: {e}")
                import traceback
                traceback.print_exc()
            
        # Vincular eventos de manera más robusta
        for widget in [button_frame, content_frame, title_label]:
            widget.bind("<Button-1>", on_button_click)
            widget.bind("<ButtonRelease-1>", on_button_click)
        
        if desc_label:
            desc_label.bind("<Button-1>", on_button_click)
            desc_label.bind("<ButtonRelease-1>", on_button_click)
        
        # Efectos hover - IDÉNTICOS AL DASHBOARD
        def on_enter(event):
            light_color = self._lighten_color(bg_color)
            button_frame.configure(bg=light_color, relief="raised", bd=3)
            content_frame.configure(bg=light_color)
            title_label.configure(bg=light_color)
            if desc_label:
                desc_label.configure(bg=light_color)
            shadow.configure(bg="#303030")
            
        def on_leave(event):
            button_frame.configure(bg=bg_color, relief="raised", bd=2)
            content_frame.configure(bg=bg_color)
            title_label.configure(bg=bg_color)
            if desc_label:
                desc_label.configure(bg=bg_color)
            shadow.configure(bg="#404040")
            
        # Aplicar eventos hover a todos los elementos
        widgets_to_bind = [button_frame, content_frame, title_label]
        if desc_label:
            widgets_to_bind.append(desc_label)
            
        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def _lighten_color(self, color):
        """Aclara un color hex - IDÉNTICO AL DASHBOARD."""
        color_map = {
            "#F44336": "#EF5350",  # Rojo claro
            "#2196F3": "#42A5F5",  # Azul claro
            "#FF9800": "#FFB74D",  # Naranja claro
            "#4CAF50": "#66BB6A",  # Verde claro
            "#9C27B0": "#AB47BC",  # Púrpura claro
            "#607D8B": "#78909C",  # Gris azulado claro
            "#00BCD4": "#26C6DA",  # Cian claro
            "#673AB7": "#7986CB",  # Indigo claro
            "#795548": "#8D6E63"   # Marrón claro
        }
        return color_map.get(color, color)

    def _load_data(self):
        """Carga los datos del dashboard de gastos."""
        try:
            # Obtener fechas del mes actual
            today = date.today()
            first_day = date(today.year, today.month, 1)
            if today.month == 12:
                last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            # Obtener métricas de gastos del mes actual
            expense_metrics = self.expense_service.get_expense_metrics(first_day, last_day)
            
            monthly_total = expense_metrics.get("total_amount", Decimal("0"))
            total_expenses_count = expense_metrics.get("total_expenses", 0)
            pending_amount = expense_metrics.get("pending_amount", Decimal("0"))
            
            # Calcular gastos pendientes por número (no por monto)
            all_expenses = self.expense_service.get_expenses_by_date_range(first_day, last_day)
            pending_expenses_count = len([e for e in all_expenses if e.status == "Pendiente"])
            
            # Calcular promedio
            average = monthly_total / total_expenses_count if total_expenses_count > 0 else Decimal("0")
            
            # Actualizar métricas
            self.monthly_total.update_value(f"${monthly_total:,.2f}")
            self.total_expenses.update_value(str(total_expenses_count))
            self.pending_expenses.update_value(str(pending_expenses_count))
            self.average_expense.update_value(f"${average:,.2f}")
            
        except Exception as e:
            print(f"Error al cargar datos del dashboard de gastos: {e}")
            # Valores por defecto en caso de error
            self.monthly_total.update_value("$0.00")
            self.total_expenses.update_value("0")
            self.pending_expenses.update_value("0")
            self.average_expense.update_value("$0.00")

    def _go_back_to_main(self):
        """Vuelve al dashboard principal."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('dashboard')

    # FUNCIONES DE NAVEGACIÓN A CADA CARD
    def _register_expense(self):
        """Navega al formulario de registro de gastos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses')  # Navega a la vista actual de gastos

    def _search_expenses(self):
        """Navega a la búsqueda avanzada de gastos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_search')

    def _expenses_by_apartment(self):
        """Navega a los gastos separados por apartamento."""
        messagebox.showinfo("Gastos por Apartamento", "Función en desarrollo...")

    def _category_analysis(self):
        """Navega al análisis de gastos por categoría."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_analytics')

    def _monthly_expenses(self):
        """Navega al resumen mensual de gastos."""
        messagebox.showinfo("Gastos Mensuales", "Función en desarrollo...")

    def _executive_reports(self):
        """Navega a los reportes ejecutivos."""
        messagebox.showinfo("Reportes Ejecutivos", "Función en desarrollo...")

    def refresh(self):
        """Actualiza los datos del dashboard."""
        self._load_data() 