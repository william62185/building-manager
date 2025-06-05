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
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz del dashboard."""
        # Contenedor principal OPTIMIZADO PARA PANTALLA COMPLETA
        self.configure(padding="4")

        # HEADER CON BOTÓN DE MODO CLARO/OSCURO
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Botón de modo claro/oscuro en la esquina superior derecha
        self.theme_button = tk.Button(
            header_frame,
            text="🌙 Modo Oscuro",
            font=("Segoe UI", 10, "normal"),
            bg="#6c757d",
            fg="white",
            relief="raised",
            bd=2,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self._toggle_theme
        )
        self.theme_button.pack(side=tk.RIGHT)

        # TODAS LAS MÉTRICAS EN UNA SOLA FILA - CARDS MÁS GRANDES Y RECTANGULARES
        metrics_section = ttk.LabelFrame(self, text="📊 Resumen Ejecutivo", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 6))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas de inquilinos - ESPACIADO REDUCIDO
        self.total_tenants = MetricsCard(
            all_metrics,
            title="Total Inquilinos",
            value="0",
            subtitle="Apartamentos ocupados",
            icon="🏢",
            color="primary"
        )
        self.total_tenants.pack(side=tk.LEFT, expand=True, padx=2)  # Menos espacio entre cards

        self.active_tenants = MetricsCard(
            all_metrics,
            title="Inquilinos al Día",
            value="0",
            subtitle="Pagos al corriente",
            icon="✅",
            color="success"
        )
        self.active_tenants.pack(side=tk.LEFT, expand=True, padx=2)

        self.late_tenants = MetricsCard(
            all_metrics,
            title="Pagos Pendientes",
            value="0",
            subtitle="Requieren atención",
            icon="⚠️",
            color="warning"
        )
        self.late_tenants.pack(side=tk.LEFT, expand=True, padx=2)

        # Métricas financieras - ESPACIADO REDUCIDO
        self.income_metrics = MetricsCard(
            all_metrics,
            title="Ingresos del Mes",
            value="$0",
            subtitle="vs mes anterior",
            icon="📈",
            color="success"
        )
        self.income_metrics.pack(side=tk.LEFT, expand=True, padx=2)

        self.expense_metrics = MetricsCard(
            all_metrics,
            title="Gastos del Mes",
            value="$0",
            subtitle="vs mes anterior",
            icon="📉",
            color="danger"
        )
        self.expense_metrics.pack(side=tk.LEFT, expand=True, padx=2)

        self.net_metrics = MetricsCard(
            all_metrics,
            title="Resultado Neto",
            value="$0",
            subtitle="Ingresos - Gastos",
            icon="💵",
            color="info"
        )
        self.net_metrics.pack(side=tk.LEFT, expand=True, padx=2)

        # Frame para módulos de navegación - MUCHO MÁS GRANDES
        modules_section = ttk.LabelFrame(self, text="🚀 Acceso Rápido a Módulos", padding="8")
        modules_section.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # Primera fila de botones principales - MUCHO MÁS GRANDES
        first_row = ttk.Frame(modules_section)
        first_row.pack(fill=tk.BOTH, expand=True, pady=(2, 4))

        # Crear botones con sombra personalizada - COLORES DINÁMICOS
        bg_color, fg_color = self._get_button_colors("tenants")
        self._create_shadow_button(
            first_row, "👥 Inquilinos\nGestionar inquilinos", 
            bg_color, fg_color, lambda: self._navigate_to_module("tenants"), "tenants"
        )

        bg_color, fg_color = self._get_button_colors("payments")
        self._create_shadow_button(
            first_row, "💰 Pagos\nRegistrar pagos", 
            bg_color, fg_color, lambda: self._navigate_to_module("payments"), "payments"
        )

        bg_color, fg_color = self._get_button_colors("expenses")
        self._create_shadow_button(
            first_row, "📊 Gastos\nAdministrar gastos", 
            bg_color, fg_color, lambda: self._navigate_to_module("expenses"), "expenses"
        )

        bg_color, fg_color = self._get_button_colors("reports")
        self._create_shadow_button(
            first_row, "📋 Reportes\nGenerar reportes", 
            bg_color, fg_color, lambda: self._navigate_to_module("reports"), "reports"
        )

        # Segunda fila de botones adicionales - MUCHO MÁS GRANDES
        second_row = ttk.Frame(modules_section)
        second_row.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        # Crear botones de segunda fila con sombra - COLORES DINÁMICOS
        bg_color, fg_color = self._get_button_colors("maintenance")
        self._create_shadow_button(
            second_row, "🔧 Mantenimiento\nTareas pendientes", 
            bg_color, fg_color, lambda: self._navigate_to_module("maintenance"), "maintenance"
        )

        bg_color, fg_color = self._get_button_colors("contacts")
        self._create_shadow_button(
            second_row, "📞 Contactos\nDirectorio completo", 
            bg_color, fg_color, lambda: self._navigate_to_module("contacts"), "contacts"
        )

        bg_color, fg_color = self._get_button_colors("settings")
        self._create_shadow_button(
            second_row, "⚙️ Configuración\nAjustes del sistema", 
            bg_color, fg_color, lambda: self._navigate_to_module("settings"), "settings"
        )

        bg_color, fg_color = self._get_button_colors("analytics")
        self._create_shadow_button(
            second_row, "📈 Análisis\nMétricas avanzadas", 
            bg_color, fg_color, lambda: self._navigate_to_module("analytics"), "analytics"
        )

    def _create_shadow_button(self, parent, text, bg_color, fg_color, command, module_id=None):
        """Crea un botón con efecto de sombra y tipografía mejorada."""
        # Frame contenedor para el efecto de sombra
        shadow_frame = ttk.Frame(parent)
        shadow_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=2)
        
        # Frame de sombra (fondo gris desplazado)
        shadow = tk.Frame(
            shadow_frame,
            bg=self._get_shadow_color(),  # Color de sombra dinámico
            relief="flat"
        )
        shadow.place(x=3, y=3, relwidth=1, relheight=1)
        
        # Frame principal del botón para contener el contenido - COLORES INICIALES ASEGURADOS
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
        
        # Contenedor interno para centrar el contenido - COLOR INICIAL ASEGURADO
        content_frame = tk.Frame(button_frame, bg=bg_color)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título del módulo (más grande) - COLORES INICIALES ASEGURADOS
        title_label = tk.Label(
            content_frame,
            text=module_name,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 16, "bold"),  # Más grande para el título
            cursor="hand2"
        )
        title_label.pack()
        
        # Descripción (más pequeña y diferente estilo) - COLORES INICIALES ASEGURADOS
        desc_label = None  # Inicializar como None
        if description:
            desc_label = tk.Label(
                content_frame,
                text=description,
                bg=bg_color,
                fg=fg_color,
                font=("Segoe UI", 11, "normal"),  # Más pequeña y normal (no bold)
                cursor="hand2"
            )
            desc_label.pack(pady=(2, 0))
        
        # FORZAR COLORES INMEDIATAMENTE - SOLUCION DEFINITIVA
        # Aplicar colores inmediatamente y múltiples veces para evitar el problema del blanco
        for _ in range(3):  # Triple aplicación
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
        self.after(10, force_colors_delayed)   # 10ms después
        self.after(50, force_colors_delayed)   # 50ms después
        self.after(100, force_colors_delayed)  # 100ms después
        
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
        
        # Efectos hover - CORREGIDOS
        def on_enter(event):
            light_color = self._lighten_color(bg_color)
            button_frame.configure(bg=light_color, relief="raised", bd=3)
            content_frame.configure(bg=light_color)
            title_label.configure(bg=light_color)
            if desc_label:  # Usar desc_label
                desc_label.configure(bg=light_color)
            shadow.configure(bg="#303030")  # Sombra más oscura
            
        def on_leave(event):
            button_frame.configure(bg=bg_color, relief="raised", bd=2)
            content_frame.configure(bg=bg_color)
            title_label.configure(bg=bg_color)
            if desc_label:  # Usar desc_label
                desc_label.configure(bg=bg_color)
            shadow.configure(bg="#404040")  # Sombra normal
            
        def on_click(event):
            button_frame.configure(relief="sunken", bd=1)
            shadow.configure(bg="#202020")  # Sombra muy oscura
            
        def on_release(event):
            button_frame.configure(relief="raised", bd=2)
            shadow.configure(bg="#404040")  # Sombra normal
            
        # Aplicar eventos hover a todos los elementos
        widgets_to_bind = [button_frame, content_frame, title_label]
        if desc_label:
            widgets_to_bind.append(desc_label)
            
        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
        # Guardar referencias para actualización dinámica de tema
        if module_id:
            button_info = {
                "module_id": module_id,
                "shadow": shadow,
                "button_frame": button_frame,
                "content_frame": content_frame,
                "title_label": title_label,
                "desc_label": desc_label,
                "bg_color": bg_color,
                "fg_color": fg_color
            }
            self.module_buttons.append(button_info)

    def _lighten_color(self, color):
        """Aclara un color hex."""
        color_map = {
            "#007bff": "#1a8cff",
            "#28a745": "#3cbf5a", 
            "#ffc107": "#ffcd39",
            "#17a2b8": "#2bb5c9",
            "#6f42c1": "#8a5bd4",  # Púrpura claro
            "#dc3545": "#e74c3c",
            "#fd7e14": "#ff8c42"   # Naranja claro
        }
        return color_map.get(color, color)
        
    def _darken_color(self, color):
        """Oscurece un color hex."""
        color_map = {
            "#007bff": "#0056b3",
            "#28a745": "#1e7e34",
            "#ffc107": "#d39e00", 
            "#17a2b8": "#117a8b",
            "#6f42c1": "#5a32a3",  # Púrpura oscuro
            "#dc3545": "#bd2130",
            "#fd7e14": "#e8590c"   # Naranja oscuro
        }
        return color_map.get(color, color)

    def _navigate_to_module(self, module_name):
        """Navega a un módulo específico."""
        # Obtener la ventana principal
        main_window = self.winfo_toplevel()
        
        # Mapear nombres de módulos a los métodos de navegación
        module_map = {
            "tenants": lambda: self._show_tenants_view(main_window),
            "payments": lambda: self._show_payments_view(main_window),
            "expenses": lambda: self._show_expenses_view(main_window),
            "reports": lambda: self._show_reports_view(main_window),
            "maintenance": lambda: self._show_maintenance_view(main_window),
            "contacts": lambda: self._show_contacts_view(main_window),
            "settings": lambda: self._show_settings_view(main_window),
            "analytics": lambda: self._show_analytics_view(main_window)
        }
        
        # Ejecutar la navegación si existe
        if module_name in module_map:
            print(f"DEBUG: Ejecutando función para {module_name}")
            module_map[module_name]()
        else:
            # Para módulos no implementados, mostrar mensaje
            print(f"DEBUG: Módulo {module_name} no implementado")
            tk.messagebox.showinfo(
                "Próximamente", 
                f"El módulo '{module_name}' estará disponible en una próxima actualización."
            )

    def _show_tenants_view(self, main_window):
        """Navega al dashboard de inquilinos."""
        if hasattr(main_window, '_show_view'):
            main_window._show_view('tenants')

    def _show_payments_view(self, main_window):
        """Navega al dashboard de pagos."""
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_dashboard')

    def _show_expenses_view(self, main_window):
        """Navega al dashboard de gastos."""
        if hasattr(main_window, '_show_view'):
            main_window._show_view('expenses_dashboard')

    def _show_reports_view(self, main_window):
        """Navega a la vista de reportes (por implementar)."""
        tk.messagebox.showinfo(
            "Próximamente", 
            "El módulo de reportes estará disponible en una próxima actualización."
        )

    def _show_maintenance_view(self, main_window):
        """Navega a la vista de mantenimiento (por implementar)."""
        tk.messagebox.showinfo(
            "Próximamente", 
            "El módulo de mantenimiento estará disponible en una próxima actualización."
        )

    def _show_contacts_view(self, main_window):
        """Navega a la vista de contactos (por implementar)."""
        tk.messagebox.showinfo(
            "Próximamente", 
            "El módulo de contactos estará disponible en una próxima actualización."
        )

    def _show_settings_view(self, main_window):
        """Navega a la vista de configuración (por implementar)."""
        tk.messagebox.showinfo(
            "Próximamente", 
            "El módulo de configuración estará disponible en una próxima actualización."
        )

    def _show_analytics_view(self, main_window):
        """Navega a la vista de análisis (por implementar)."""
        tk.messagebox.showinfo(
            "Próximamente", 
            "El módulo de análisis estará disponible en una próxima actualización."
        )

    def _load_data(self):
        """Carga los datos del dashboard."""
        today = date.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        # Métricas de inquilinos
        tenant_metrics = self.tenant_service.get_tenant_metrics()
        total_tenants = tenant_metrics["total_tenants"]
        active_tenants = tenant_metrics["active_tenants"]
        late_tenants = total_tenants - active_tenants

        self.total_tenants.update_value(str(total_tenants))
        self.active_tenants.update_value(str(active_tenants))
        self.late_tenants.update_value(str(late_tenants))

        # Métricas financieras del mes actual
        current_income = self.payment_service.get_payment_metrics(first_day, last_day)["total_amount"]
        current_expenses = self.expense_service.get_expense_metrics(first_day, last_day)["total_amount"]
        net_result = current_income - current_expenses

        # Métricas del mes anterior
        prev_first_day = date(today.year, today.month - 1, 1)
        prev_last_day = first_day - timedelta(days=1)
        prev_income = self.payment_service.get_payment_metrics(prev_first_day, prev_last_day)["total_amount"]
        prev_expenses = self.expense_service.get_expense_metrics(prev_first_day, prev_last_day)["total_amount"]

        # Calcular diferencias porcentuales
        income_diff = current_income - prev_income
        income_percent = (income_diff / prev_income * 100) if prev_income else 0
        expense_diff = current_expenses - prev_expenses
        expense_percent = (expense_diff / prev_expenses * 100) if prev_expenses else 0

        # Actualizar métricas financieras
        self.income_metrics.update_value(f"${current_income:,.2f}")
        self.income_metrics.update_subtitle(
            f"{'↑' if income_diff >= 0 else '↓'} {abs(income_percent):.1f}% vs mes anterior"
        )

        self.expense_metrics.update_value(f"${current_expenses:,.2f}")
        self.expense_metrics.update_subtitle(
            f"{'↑' if expense_diff >= 0 else '↓'} {abs(expense_percent):.1f}% vs mes anterior"
        )

        self.net_metrics.update_value(f"${net_result:,.2f}")
        self.net_metrics.update_subtitle(
            "Balance del mes actual"
        )

    def _toggle_theme(self):
        """Alterna entre modo claro y oscuro."""
        self.dark_mode = not self.dark_mode
        
        # Obtener la ventana principal y actualizar todo el tema
        main_window = self.winfo_toplevel()
        
        if hasattr(main_window, 'update_theme'):
            # Usar el método de actualización de tema de MainWindow
            main_window.update_theme(self.dark_mode)
        else:
            # Fallback para compatibilidad
            if self.dark_mode:
                main_window.configure(bg="#2b2b2b")
            else:
                main_window.configure(bg="#dee2e6")
        
        # Actualizar el botón de tema
        if self.dark_mode:
            self.theme_button.configure(
                text="☀️ Modo Claro",
                bg="#ffc107",
                fg="black"
            )
        else:
            self.theme_button.configure(
                text="🌙 Modo Oscuro",
                bg="#6c757d",
                fg="white"
            )
            
        # Actualizar todos los botones de módulos
        self._update_all_buttons()
    
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