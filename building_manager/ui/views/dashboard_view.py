import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any

from ..components import MetricsCard, DataTable
from ...services import TenantService, PaymentService, ExpenseService

class DashboardView(ttk.Frame):
    """Vista principal del dashboard que muestra métricas y resúmenes."""
    def __init__(self, master: Any):
        super().__init__(master)
        self.tenant_service = TenantService()
        self.payment_service = PaymentService()
        self.expense_service = ExpenseService()
        
        # Variable para el modo oscuro
        self.dark_mode = False
        
        # Lista para almacenar referencias de botones para actualización dinámica
        self.module_buttons = []
        
        self.setup_ui()
        self._load_data()

    def setup_ui(self):
        """Configura la interfaz del dashboard."""
        # Título de Resumen Ejecutivo con icono
        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        self.summary_icon = ttk.Label(
            self.summary_frame,
            text="📊",
            font=("Segoe UI", 20)
        )
        self.summary_icon.pack(side=tk.LEFT)
        
        self.summary_label = ttk.Label(
            self.summary_frame,
            text="Resumen Ejecutivo",
            font=("Segoe UI", 16, "bold")
        )
        self.summary_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Grid de métricas
        self.metrics_frame = ttk.Frame(self)
        self.metrics_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Configurar grid
        for i in range(6):
            self.metrics_frame.columnconfigure(i, weight=1)
        
        # Métricas
        metrics_data = [
            ("🏢", "Total Inquilinos", "3", "Apartamentos ocupados"),
            ("✓", "Inquilinos al Día", "0", "Pagos al corriente"),
            ("⚠", "Pagos Pendientes", "3", "Requieren atención"),
            ("📈", "Ingresos del Mes", "$0.00", "↑ 0.0% vs mes anterior"),
            ("📉", "Gastos del Mes", "$0.00", "↑ 0.0% vs mes anterior"),
            ("💰", "Resultado Neto", "$0.00", "Balance del mes actual")
        ]
        
        for i, (icon, title, value, subtitle) in enumerate(metrics_data):
            metric = MetricsCard(
                self.metrics_frame,
                title,
                value,
                subtitle=subtitle,
                icon=icon
            )
            metric.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        
        # Título de Acceso Rápido a Módulos con icono
        self.modules_header = ttk.Frame(self)
        self.modules_header.pack(fill=tk.X, padx=20, pady=(20, 5))
        
        self.modules_icon = ttk.Label(
            self.modules_header,
            text="🔷",
            font=("Segoe UI", 20)
        )
        self.modules_icon.pack(side=tk.LEFT)
        
        self.modules_label = ttk.Label(
            self.modules_header,
            text="Acceso Rápido a Módulos",
            font=("Segoe UI", 16, "bold")
        )
        self.modules_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Grid de módulos
        self.modules_frame = ttk.Frame(self)
        self.modules_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Configurar grid de módulos
        for i in range(4):
            self.modules_frame.columnconfigure(i, weight=1)
        self.modules_frame.rowconfigure(0, weight=1)
        self.modules_frame.rowconfigure(1, weight=1)
        
        # Módulos
        modules_data = [
            ("👥", "Inquilinos", "Gestionar inquilinos", 0, 0),
            ("💰", "Pagos", "Registrar pagos", 0, 1),
            ("📊", "Gastos", "Administrar gastos", 0, 2),
            ("📋", "Reportes", "Generar reportes", 0, 3),
            ("🔧", "Mantenimiento", "Tareas pendientes", 1, 0),
            ("👤", "Contactos", "Directorio completo", 1, 1),
            ("⚙️", "Configuración", "Ajustes del sistema", 1, 2),
            ("📈", "Análisis", "Métricas avanzadas", 1, 3)
        ]
        
        for icon, title, subtitle, row, col in modules_data:
            frame = ttk.Frame(self.modules_frame, relief="solid", borderwidth=1)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Icono del módulo
            module_icon = ttk.Label(
                frame,
                text=icon,
                font=("Segoe UI", 24)
            )
            module_icon.pack(pady=(10, 5))
            
            # Título del módulo
            module_title = ttk.Label(
                frame,
                text=title,
                font=("Segoe UI", 14, "bold")
            )
            module_title.pack(pady=(0, 5))
            
            # Subtítulo del módulo
            module_subtitle = ttk.Label(
                frame,
                text=subtitle,
                font=("Segoe UI", 11)
            )
            module_subtitle.pack(pady=(0, 10))
            
            # Configurar hover
            frame.bind("<Enter>", lambda e, f=frame: f.configure(relief="sunken"))
            frame.bind("<Leave>", lambda e, f=frame: f.configure(relief="solid"))

    def _load_data(self):
        """Carga los datos del dashboard."""
        try:
            today = date.today()
            first_day = date(today.year, today.month, 1)
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)

            # Métricas de inquilinos
            tenant_metrics = self.tenant_service.get_tenant_metrics()
            total_tenants = tenant_metrics.get("total_tenants", 0)
            active_tenants = tenant_metrics.get("active_tenants", 0)
            late_tenants = total_tenants - active_tenants

            self.total_tenants.update_value(str(total_tenants))
            self.up_to_date.update_value(str(active_tenants))
            self.pending_payments.update_value(str(late_tenants))

            # Métricas financieras
            current_income = self.payment_service.get_payment_metrics(first_day, last_day).get("total_amount", Decimal("0"))
            current_expenses = self.expense_service.get_expense_metrics(first_day, last_day).get("total_amount", Decimal("0"))
            net_result = current_income - current_expenses

            # Métricas del mes anterior
            prev_first_day = date(today.year, today.month - 1, 1)
            prev_last_day = first_day - timedelta(days=1)
            prev_income = self.payment_service.get_payment_metrics(prev_first_day, prev_last_day).get("total_amount", Decimal("0"))
            prev_expenses = self.expense_service.get_expense_metrics(prev_first_day, prev_last_day).get("total_amount", Decimal("0"))

            # Calcular diferencias porcentuales
            income_diff = current_income - prev_income
            income_percent = (income_diff / prev_income * 100) if prev_income else Decimal("0")
            expense_diff = current_expenses - prev_expenses
            expense_percent = (expense_diff / prev_expenses * 100) if prev_expenses else Decimal("0")

            # Actualizar métricas financieras
            self.monthly_income.update_value(f"${current_income:,.2f}")
            self.monthly_income.update_subtitle(f"{'↑' if income_diff >= 0 else '↓'} {abs(income_percent):.1f}% vs mes anterior")
            
            self.monthly_expenses.update_value(f"${current_expenses:,.2f}")
            self.monthly_expenses.update_subtitle(f"{'↑' if expense_diff >= 0 else '↓'} {abs(expense_percent):.1f}% vs mes anterior")
            
            self.net_result.update_value(f"${net_result:,.2f}")

        except Exception as e:
            print(f"Error al cargar datos del dashboard: {e}")

    def _toggle_dark_mode(self):
        """Alterna entre modo claro y oscuro."""
        self.dark_mode = not self.dark_mode
        # Implementar cambio de tema aquí

    def _show_tenants_view(self):
        """Navega a la vista de inquilinos."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("tenants")

    def _show_payments_view(self):
        """Navega a la vista de pagos."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("payments")

    def _show_expenses_view(self):
        """Navega a la vista de gastos."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("expenses")

    def _show_reports_view(self):
        """Navega a la vista de reportes."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("reports")

    def _show_maintenance_view(self):
        """Navega a la vista de mantenimiento."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("maintenance")

    def _show_contacts_view(self):
        """Navega a la vista de contactos."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("contacts")

    def _show_settings_view(self):
        """Navega a la vista de configuración."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("settings")

    def _show_analytics_view(self):
        """Navega a la vista de análisis."""
        if hasattr(self.master, "show_view"):
            self.master.show_view("analytics")

    def _get_shadow_color(self):
        """Retorna el color de sombra según el tema actual."""
        return "#111111" if self.dark_mode else "#404040"
    
    def _get_button_colors(self, module):
        """Retorna los colores de los botones según el tema actual."""
        if self.dark_mode:
            # Colores más sutiles y elegantes para modo oscuro
            colors = {
                "tenants": ("#1e3a8a", "white"),      # Azul oscuro más suave
                "payments": ("#166534", "white"),     # Verde oscuro más suave
                "expenses": ("#a16207", "white"),     # Amarillo/mostaza oscuro 
                "reports": ("#155e75", "white"),      # Cyan oscuro más suave
                "maintenance": ("#155e75", "white"),  # Cyan oscuro más suave
                "contacts": ("#ea580c", "white"),     # Naranja más suave
                "settings": ("#7c3aed", "white"),     # Púrpura más vibrante
                "analytics": ("#be123c", "white")     # Rojo más suave
            }
        else:
            # Colores normales para modo claro
            colors = {
                "tenants": ("#007bff", "white"),
                "payments": ("#28a745", "white"),
                "expenses": ("#ffc107", "black"),
                "reports": ("#17a2b8", "white"),
                "maintenance": ("#17a2b8", "white"),
                "contacts": ("#fd7e14", "white"),
                "settings": ("#6f42c1", "white"),
                "analytics": ("#dc3545", "white")
            }
        return colors.get(module, ("#6c757d", "white"))

    def _update_all_buttons(self):
        """Actualiza todos los botones de módulos con los colores del tema actual."""
        for button_info in self.module_buttons:
            module_id = button_info["module_id"]
            
            # Obtener nuevos colores para el módulo
            new_bg_color, new_fg_color = self._get_button_colors(module_id)
            
            # Actualizar referencias de colores
            button_info["bg_color"] = new_bg_color
            button_info["fg_color"] = new_fg_color
            
            # Actualizar widgets
            try:
                # Actualizar colores de fondo y texto
                button_info["button_frame"].configure(bg=new_bg_color)
                button_info["content_frame"].configure(bg=new_bg_color)
                button_info["title_label"].configure(bg=new_bg_color, fg=new_fg_color)
                
                if button_info["desc_label"]:
                    button_info["desc_label"].configure(bg=new_bg_color, fg=new_fg_color)
                
                # Actualizar sombra
                button_info["shadow"].configure(bg=self._get_shadow_color())
                
            except tk.TclError:
                # Widget ya no existe, ignorar
                pass

    def refresh(self):
        """Actualiza los datos del dashboard."""
        self._load_data()

    def refresh_theme(self):
        """Actualiza los widgets cuando cambia el tema."""
        # Los widgets ttk se actualizan automáticamente con el nuevo tema
        # Solo necesitamos actualizar widgets personalizados si los hubiera
        pass 