"""
Ventana principal profesional para Building Manager
Diseño moderno con navegación elegante
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable
from tkinter import messagebox
from datetime import datetime
import os
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard, ModernSeparator, ModernMetricCard, DetailedMetricCard
from manager.app.services.tenant_service import TenantService
from manager.app.services.payment_service import PaymentService
from manager.app.services.expense_service import ExpenseService
from .payments_view import PaymentsView
from .tenants_view import TenantsView
from .expenses_view import ExpensesView
from .apartment_management_view import ApartmentManagementView
from .building_setup_view import BuildingSetupView
from .apartment_form_view import ApartmentFormView
from .apartments_list_view import ApartmentsListView
from .building_management_view import BuildingManagementView
from .deactivate_tenant_view import DeactivateTenantView

class MainWindow:
    """Ventana principal con diseño profesional"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_view = None
        self.views = {}
        
        self._setup_window()
        self._create_layout()
        
    def _setup_window(self):
        """Configura la ventana principal"""
        self.root.title("Building Manager Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Maximizar la ventana al inicio
        self.root.state('zoomed')  # Windows
        # Para macOS y Linux sería: self.root.attributes('-zoomed', True)
        
        # Configurar estilos
        self.root.configure(**theme_manager.get_style("window"))
        
        # Icono de la aplicación (puedes cambiar por un .ico)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass  # Si no existe el icono, continúa sin él
        
        # Centrar ventana si no se puede maximizar
        self._center_window()
    
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Obtener dimensiones de la ventana
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        
        # Calcular posición para centrar
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Solo centrar si no está maximizada
        if self.root.state() != 'zoomed':
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _create_layout(self):
        """Crea el layout principal con sidebar y contenido"""
        # Frame principal
        main_frame = tk.Frame(self.root, **theme_manager.get_style("frame"))
        main_frame.pack(fill="both", expand=True)
        
        # Sidebar de navegación
        self._create_sidebar(main_frame)
        
        # Área de contenido principal
        self._create_content_area(main_frame)
    
    def _create_sidebar(self, parent):
        """Crea la barra lateral de navegación"""
        self.sidebar = tk.Frame(
            parent,
            width=280,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_secondary"],
            relief="flat"
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Header del sidebar
        self._create_sidebar_header()
        
        # Separador
        ModernSeparator(self.sidebar, orientation="horizontal")
        
        # Menú de navegación
        self._create_navigation_menu()
        
        # Footer del sidebar
        self._create_sidebar_footer()
    
    def _create_sidebar_header(self):
        """Crea el header del sidebar con logo y título"""
        header_frame = tk.Frame(
            self.sidebar,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_secondary"],
            height=80
        )
        header_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        header_frame.pack_propagate(False)
        
        # Logo/Icono de la aplicación
        logo_frame = tk.Frame(header_frame, bg=header_frame.cget("bg"))
        logo_frame.pack(side="left")
        
        logo_label = tk.Label(
            logo_frame,
            text="🏢",
            font=("Segoe UI Symbol", 28),
            bg=header_frame.cget("bg"),
            fg=theme_manager.themes[theme_manager.current_theme]["text_accent"]
        )
        logo_label.pack()
        
        # Texto del título
        title_frame = tk.Frame(header_frame, bg=header_frame.cget("bg"))
        title_frame.pack(side="left", fill="both", expand=True, padx=(Spacing.MD, 0))
        
        title_label = tk.Label(
            title_frame,
            text="Building\nManager",
            font=("Segoe UI", 14, "bold"),
            bg=header_frame.cget("bg"),
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            anchor="w",
            justify="left"
        )
        title_label.pack(anchor="w")
        
        version_label = tk.Label(
            title_frame,
            text="v1.0 Pro",
            font=("Segoe UI", 9),
            bg=header_frame.cget("bg"),
            fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"],
            anchor="w"
        )
        version_label.pack(anchor="w")
    
    def _create_navigation_menu(self):
        """Crea el menú de navegación principal"""
        nav_frame = tk.Frame(
            self.sidebar,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_secondary"]
        )
        nav_frame.pack(fill="both", expand=True, padx=Spacing.MD)
        
        # Elementos del menú
        menu_items = [
            {
                "text": "Dashboard",
                "icon": Icons.DASHBOARD,
                "command": lambda: self._navigate_to("dashboard"),
                "active": True
            },
            {
                "text": "Inquilinos",
                "icon": Icons.TENANTS,
                "command": lambda: self._navigate_to("tenants"),
                "active": False
            },
            {
                "text": "Pagos",
                "icon": Icons.PAYMENTS,
                "command": lambda: self._navigate_to("payments"),
                "active": False
            },
            {
                "text": "Gastos",
                "icon": Icons.EXPENSES,
                "command": lambda: self._navigate_to("expenses"),
                "active": False
            },
            {
                "text": "Administración",
                "icon": "🔧",
                "command": lambda: self._navigate_to("administration"),
                "active": False
            },
            {
                "text": "Reportes",
                "icon": Icons.REPORTS,
                "command": lambda: self._navigate_to("reports"),
                "active": False
            }
        ]
        
        self.nav_buttons = {}
        
        for item in menu_items:
            btn_frame = self._create_nav_button(nav_frame, item)
            self.nav_buttons[item["text"].lower()] = btn_frame
    
    def _create_nav_button(self, parent, item: Dict[str, Any]) -> tk.Frame:
        """Crea un botón de navegación elegante"""
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Frame del botón
        btn_frame = tk.Frame(
            parent,
            bg=theme["bg_accent"] if item.get("active") else theme["bg_secondary"],
            relief="flat",
            height=50
        )
        btn_frame.pack(fill="x", pady=(0, Spacing.XS))
        btn_frame.pack_propagate(False)
        
        # Contenedor interno con padding
        inner_frame = tk.Frame(
            btn_frame,
            bg=btn_frame.cget("bg")
        )
        inner_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Icono
        icon_label = tk.Label(
            inner_frame,
            text=item["icon"],
            font=("Segoe UI Symbol", 16),
            bg=inner_frame.cget("bg"),
            fg=theme["text_accent"] if item.get("active") else theme["text_primary"],
            width=3
        )
        icon_label.pack(side="left")
        
        # Texto
        text_label = tk.Label(
            inner_frame,
            text=item["text"],
            font=("Segoe UI", 11, "bold" if item.get("active") else "normal"),
            bg=inner_frame.cget("bg"),
            fg=theme["text_accent"] if item.get("active") else theme["text_primary"],
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True, padx=(Spacing.MD, 0))
        
        # Efectos de hover y click
        def on_click(event=None):
            item["command"]()
        
        def on_enter(event):
            if not item.get("active"):
                btn_frame.configure(bg=theme["bg_tertiary"])
                inner_frame.configure(bg=theme["bg_tertiary"])
                icon_label.configure(bg=theme["bg_tertiary"])
                text_label.configure(bg=theme["bg_tertiary"])
        
        def on_leave(event):
            if not item.get("active"):
                original_bg = theme["bg_secondary"]
                btn_frame.configure(bg=original_bg)
                inner_frame.configure(bg=original_bg)
                icon_label.configure(bg=original_bg)
                text_label.configure(bg=original_bg)
        
        # Bind events
        for widget in [btn_frame, inner_frame, icon_label, text_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        
        return btn_frame
    
    def _create_sidebar_footer(self):
        """Crea el footer del sidebar"""
        footer_frame = tk.Frame(
            self.sidebar,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_secondary"],
            height=100
        )
        footer_frame.pack(side="bottom", fill="x", padx=Spacing.MD, pady=Spacing.MD)
        footer_frame.pack_propagate(False)
        
        # Separador
        separator = tk.Frame(
            footer_frame,
            height=1,
            bg=theme_manager.themes[theme_manager.current_theme]["border_light"]
        )
        separator.pack(fill="x", pady=(0, Spacing.MD))
        
        # Botón de configuración
        settings_btn = self._create_nav_button(
            footer_frame,
            {
                "text": "Configuración",
                "icon": Icons.SETTINGS,
                "command": lambda: self._navigate_to("settings"),
                "active": False
            }
        )
    
    def _create_content_area(self, parent):
        """Crea el área de contenido principal"""
        # Frame principal de contenido
        self.content_frame = tk.Frame(
            parent,
            **theme_manager.get_style("frame")
        )
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Header del contenido
        self._create_content_header()
        
        # Área de vistas
        self.views_container = tk.Frame(
            self.content_frame,
            **theme_manager.get_style("frame")
        )
        self.views_container.pack(fill="both", expand=True, padx=Spacing.XL, pady=(0, Spacing.XL))
        
        # Cargar vista inicial
        self._navigate_to("dashboard")
    
    def _create_content_header(self):
        """Crea el header del área de contenido"""
        header_frame = tk.Frame(
            self.content_frame,
            **theme_manager.get_style("frame"),
            height=80
        )
        header_frame.pack(fill="x", padx=Spacing.XL, pady=Spacing.XL)
        header_frame.pack_propagate(False)
        
        # Título de la vista actual
        self.page_title = tk.Label(
            header_frame,
            text="Dashboard",
            **theme_manager.get_style("label_title")
        )
        self.page_title.configure(font=("Segoe UI", 24, "bold"))
        self.page_title.pack(side="left", anchor="w")
        
        # Área de acciones del header
        actions_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        actions_frame.pack(side="right")
        
        # Botón de notificaciones
        notif_btn = tk.Button(
            actions_frame,
            text=f"{Icons.NOTIFICATION}",
            font=("Segoe UI Symbol", 16),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            relief="solid",
            bd=1,
            width=3,
            cursor="hand2"
        )
        notif_btn.pack(side="right", padx=(Spacing.SM, 0))
        
        # Usuario actual
        user_frame = tk.Frame(actions_frame, **theme_manager.get_style("frame"))
        user_frame.pack(side="right", padx=(0, Spacing.MD))
        
        user_label = tk.Label(
            user_frame,
            text=f"{Icons.TENANT_PROFILE} Admin",
            **theme_manager.get_style("label_body")
        )
        user_label.pack()
    
    def _navigate_to(self, view_name: str):
        """Navega a una vista específica"""
        # Guardar la vista actual
        self._current_view = view_name
        
        # Actualizar estado de botones de navegación
        self._update_nav_buttons(view_name)
        
        # Actualizar título
        titles = {
            "dashboard": "Dashboard",
            "tenants": "Gestión de Inquilinos",
            "payments": "Gestión de Pagos",
            "expenses": "Gestión de Gastos",
            "administration": "Administración",
            "reports": "Reportes y Análisis",
            "settings": "Configuración"
        }
        
        self.page_title.configure(text=titles.get(view_name, "Building Manager"))
        
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Cargar nueva vista
        self._load_view(view_name)
        
        # Forzar actualización especial para la vista de inquilinos
        if view_name == "tenants":
            self.root.after(500, self._force_tenants_refresh)
    
    def _update_nav_buttons(self, active_view: str):
        """Actualiza el estado visual de los botones de navegación"""
        theme = theme_manager.themes[theme_manager.current_theme]
        
        for view_name, btn_frame in self.nav_buttons.items():
            is_active = view_name == active_view
            
            # Colores según estado
            bg_color = theme["bg_accent"] if is_active else theme["bg_secondary"]
            text_color = theme["text_accent"] if is_active else theme["text_primary"]
            
            # Actualizar frame principal
            btn_frame.configure(bg=bg_color)
            
            # Actualizar todos los widgets hijos
            for child in btn_frame.winfo_children():
                child.configure(bg=bg_color)
                for grandchild in child.winfo_children():
                    grandchild.configure(bg=bg_color, fg=text_color)
    
    def _load_view(self, view_name: str):
        """Carga una vista específica"""
        if view_name == "dashboard":
            self._create_dashboard_view()
        elif view_name == "tenants":
            self._create_tenants_view()
            # Forzar actualización después de cargar la vista de inquilinos
            self.root.after(100, self.root.update_idletasks)
            self.root.after(200, self.root.update)
        elif view_name == "payments":
            payments_view = PaymentsView(
                self.views_container, 
                on_back=lambda: self._navigate_to("dashboard"),
                on_payment_saved=self.refresh_tenants_view
            )
            payments_view.pack(fill="both", expand=True)
        elif view_name == "expenses":
            expenses_view = ExpensesView(self.views_container, on_back=lambda: self._navigate_to("dashboard"))
            expenses_view.pack(fill="both", expand=True)
        elif view_name == "administration":
            self._create_administration_view()
        elif view_name == "reports":
            self._create_placeholder_view("Módulo de Reportes", "Análisis y reportes del edificio")
        elif view_name == "settings":
            self._create_placeholder_view("Configuración", "Configuración del sistema")
    
    def _create_dashboard_view(self):
        """Crea la vista del dashboard"""
        # Grid de métricas principales
        metrics_frame = tk.Frame(self.views_container, **theme_manager.get_style("frame"))
        metrics_frame.pack(fill="x", pady=(0, Spacing.XL))
        
        # Fila de métricas
        metrics_row = tk.Frame(metrics_frame, **theme_manager.get_style("frame"))
        metrics_row.pack(fill="x")
        
        # Métrica 1: Total Inquilinos con detalles
        tenant_stats = self._get_tenant_statistics()
        metric1 = DetailedMetricCard(
            metrics_row,
            title="Total Inquilinos",
            total_value=str(tenant_stats["total"]),
            details=[
                {
                    "label": "Al día",
                    "value": tenant_stats["al_dia"],
                    "color": "#10b981"  # Verde
                },
                {
                    "label": "En mora",
                    "value": tenant_stats["moroso"],
                    "color": "#ef4444"  # Rojo
                }
            ],
            icon=Icons.TENANTS,
            color_theme="primary"
        )
        metric1.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Métrica 2: Pagos Pendientes
        metric2 = ModernMetricCard(
            metrics_row,
            title="Pagos Pendientes",
            value=f"${int(2450):,}",
            icon=Icons.PAYMENT_PENDING,
            color_theme="warning"
        )
        metric2.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Métrica 3: Ingresos del Mes (real)
        ingresos_mes = self._get_payments_of_current_month()
        metric3 = ModernMetricCard(
            metrics_row,
            title="Ingresos del Mes",
            value=f"${int(ingresos_mes):,}",
            icon=Icons.PAYMENT_RECEIVED,
            color_theme="success"
        )
        metric3.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Métrica 4: Gastos del Mes (ya está bien)
        gastos_mes = self._get_expenses_of_current_month()
        metric4 = ModernMetricCard(
            metrics_row,
            title="Gastos del Mes", 
            value=f"${int(gastos_mes):,}",
            icon=Icons.EXPENSES,
            color_theme="error"
        )
        metric4.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Métrica 5: Saldo Neto del Mes (ingresos reales - gastos reales)
        saldo_neto = ingresos_mes - gastos_mes
        if saldo_neto >= 0:
            net_value = f"${int(saldo_neto):,}"
            net_theme = "success"
        else:
            net_value = f"-${int(abs(saldo_neto)):,}"
            net_theme = "error"
        metric5 = ModernMetricCard(
            metrics_row,
            title="Saldo Neto del Mes",
            value=net_value,
            icon="💼",
            color_theme=net_theme
        )
        metric5.pack(side="left", fill="both", expand=True)
        
        # Separador elegante
        ModernSeparator(self.views_container)
        
        # Grid de acciones principales del administrador
        self._create_admin_actions_grid()
    
    def _create_tenants_view(self):
        """Crea la vista de inquilinos"""
        tenants_view = TenantsView(
            self.views_container,
            on_navigate=self._navigate_to,
            on_data_change=self.refresh_dashboard,  # Callback para actualizar dashboard
            on_register_payment=self.navigate_to_payments
        )
        tenants_view.pack(fill="both", expand=True)
        
        # Forzar actualización después de crear la vista
        self.root.update_idletasks()
        self.root.update()
    
    def _create_administration_view(self):
        """Crea la vista de administración"""
        # Grid de acciones administrativas
        self._create_administration_actions_grid()
    
    def _create_administration_actions_grid(self):
        """Crea el grid de acciones administrativas"""
        admin_frame = tk.Frame(self.views_container, **theme_manager.get_style("frame"))
        admin_frame.pack(fill="both", expand=True)

        # Verificar si ya existe un edificio para la versión profesional
        from manager.app.services.building_service import building_service
        has_existing_building = building_service.has_buildings()

        actions_grid = [
            {
                "icon": "🏗️",
                "title": "Crear Nuevo Edificio",
                "color": "#8b5cf6",
                "action": self._show_building_setup_view,
                "enabled": not has_existing_building,  # Deshabilitar si ya existe un edificio
                "disabled_message": "Ya existe un edificio configurado"
            },
            {
                "icon": "🏢",
                "title": "Gestionar Edificio" if has_existing_building else "Gestionar Edificios",
                "color": "#6366f1",
                "action": self._show_building_management_view,
                "enabled": True
            },
            {
                "icon": "🛋️",
                "title": "Gestión de Apartamentos",
                "color": "#3b82f6",
                "action": self._show_apartment_management_view,
                "enabled": True
            },
            {
                "icon": "💾",
                "title": "Backup de Datos",
                "color": "#10b981",
                "action": lambda: self._show_placeholder_dialog("Backup de Datos", "Funcionalidad en desarrollo"),
                "enabled": True
            },
            {
                "icon": "👥",
                "title": "Desactivar Inquilino",
                "color": "#ef4444",
                "action": self._show_deactivate_tenant_form,
                "enabled": True
            },
            {
                "icon": "🔔",
                "title": "Notificaciones",
                "color": "#f59e0b",
                "action": lambda: self._show_placeholder_dialog("Gestión de Notificaciones", "Funcionalidad en desarrollo"),
                "enabled": True
            },
            {
                "icon": "⚙️",
                "title": "Gestión de Usuarios",
                "color": "#6366f1",
                "action": lambda: self._show_placeholder_dialog("Gestión de Usuarios", "Funcionalidad en desarrollo"),
                "enabled": True
            }
        ]
        
        # Crear filas de 3 tarjetas cada una
        num_columns = 3
        for i in range(0, len(actions_grid), num_columns):
            row_frame = tk.Frame(admin_frame, **theme_manager.get_style("frame"))
            row_frame.pack(fill="x", pady=Spacing.LG, padx=Spacing.LG, anchor="n")
            
            row_items = actions_grid[i:i+num_columns]
            for item in row_items:
                card = self._create_admin_action_card(
                    row_frame, item["icon"], item["title"], item["color"], 
                    item["action"], item.get("enabled", True), item.get("disabled_message", "")
                )
                card.pack(side="left", fill="both", expand=True, padx=(0, Spacing.LG))

    def _create_placeholder_view(self, title: str, subtitle: str):
        """Crea una vista placeholder"""
        card = ModernCard(
            self.views_container,
            title=title,
            subtitle=subtitle
        )
        card.pack(fill="both", expand=True)
        
        placeholder_label = tk.Label(
            card.content_frame,
            text="🚧 Módulo en desarrollo\n\nEste módulo será implementado próximamente.",
            **theme_manager.get_style("label_body"),
            justify="center"
        )
        placeholder_label.pack(expand=True)
    
    def _create_admin_actions_grid(self):
        """Crea el grid de acciones principales para el administrador"""
        # Contenedor principal optimizado para mejor uso del espacio
        main_container = tk.Frame(self.views_container, **theme_manager.get_style("frame"))
        main_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        
        # Título de la sección
        title_label = tk.Label(
            main_container,
            text="Acciones Principales",
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 18, "bold"))
        title_label.pack(anchor="w", pady=(0, Spacing.LG))
        
        # Contenedor del grid con distribución uniforme usando grid geometry
        grid_container = tk.Frame(main_container, **theme_manager.get_style("frame"))
        grid_container.pack(fill="both", expand=True)
        
        # Configurar el grid para distribución uniforme
        for i in range(3):  # 3 columnas
            grid_container.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(2):  # 2 filas
            grid_container.grid_rowconfigure(i, weight=1, uniform="row")
        
        # Datos de las cards con mejor organización
        cards_data = [
            # Primera fila
            {
                "icon": "👤", "title": "Nuevo Inquilino", 
                "color": "#2563eb", "action": lambda: self._show_new_tenant_form(),
                "row": 0, "col": 0
            },
            {
                "icon": "💰", "title": "Registrar Pago", 
                "color": "#059669", "action": lambda: self._show_register_payment_direct(),
                "row": 0, "col": 1
            },
            {
                "icon": "💸", "title": "Registrar Gasto", 
                "color": "#dc2626", "action": lambda: self._show_register_expense_direct(),
                "row": 0, "col": 2
            },
            # Segunda fila
            {
                "icon": "🔍", "title": "Buscar Inquilino", 
                "color": "#7c3aed", "action": lambda: self._show_search_dialog(),
                "row": 1, "col": 0
            },
            {
                "icon": "📊", "title": "Generar Reporte", 
                "color": "#ea580c", "action": lambda: self._navigate_to("reports"),
                "row": 1, "col": 1
            },
            {
                "icon": "⏰", "title": "Pagos Pendientes", 
                "color": "#d97706", "action": lambda: self._show_pending_payments(),
                "row": 1, "col": 2
            }
        ]
        
        # Crear las cards usando grid con dimensiones uniformes
        for card_info in cards_data:
            card = self._create_admin_action_card(
                grid_container,
                card_info["icon"],
                card_info["title"],
                card_info["color"],
                card_info["action"]
            )
            card.grid(
                row=card_info["row"],
                column=card_info["col"],
                sticky="nsew",
                padx=Spacing.XS,
                pady=Spacing.XS
            )
    
    def _show_new_tenant_form(self):
        """Muestra directamente el formulario de nuevo inquilino"""
        # Actualizar estado de botones de navegación para inquilinos
        self._update_nav_buttons("tenants")
        
        # Actualizar título
        self.page_title.configure(text="Nuevo Inquilino")
        
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Crear el formulario de nuevo inquilino directamente
        from .tenant_form_view import TenantFormView
        
        form_view = TenantFormView(
            self.views_container,
            on_back=lambda: self._navigate_to("tenants"),
            on_save_success=self.refresh_dashboard  # Callback para actualizar dashboard
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_search_dialog(self):
        """Muestra la vista de solo consulta de inquilinos (Ver detalles inquilinos)"""
        from .tenants_view import TenantsView
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        # Crear la vista de solo consulta, pasando el callback correcto
        tenants_view = TenantsView(
            self.views_container,
            on_navigate=self._navigate_to,
            on_data_change=self.refresh_dashboard,
            on_register_payment=self.navigate_to_payments
        )
        tenants_view._show_tenants_list()  # Ir directo a la vista de detalles
        tenants_view.pack(fill="both", expand=True)
    
    def _show_pending_payments(self):
        """Muestra vista de pagos pendientes"""
        # Por ahora navegar a pagos, luego se puede implementar una vista específica
        self._navigate_to("payments")

    def _show_deactivate_tenant_form(self):
        """Muestra el formulario para desactivar un inquilino"""
        from .deactivate_tenant_view import DeactivateTenantView
        
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Crear el formulario de desactivación
        deactivate_view = DeactivateTenantView(
            self.views_container,
            on_back=lambda: self._navigate_to("administration"),
            on_success=self._on_tenant_deactivated
        )
        deactivate_view.pack(fill="both", expand=True)

    def _show_apartment_management_view(self):
        """Muestra la vista de gestión de apartamentos"""
        self.page_title.configure(text="Gestión de Apartamentos")
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        apartment_view = ApartmentManagementView(self.views_container, on_navigate=self._navigate_to)
        apartment_view.pack(fill="both", expand=True)

    def _show_placeholder_dialog(self, title: str, message: str):
        """Muestra un diálogo placeholder para funcionalidades futuras"""
        messagebox.showinfo(title, f"{message}\n\nEsta funcionalidad será implementada próximamente.")

    def _on_tenant_deactivated(self):
        """Callback cuando se desactiva un inquilino exitosamente"""
        # Actualizar dashboard si hay callback
        self.refresh_dashboard()
        # Volver a administración
        self._navigate_to("administration")

    def _create_admin_action_card(self, parent, icon: str, title: str, color: str, action: Callable, enabled: bool = True, disabled_message: str = ""):
        """Crea una card de acción administrativa solo con icono y título, sin descripción"""
        style = theme_manager.get_style("card").copy()
        style["bd"] = 2
        style["relief"] = "raised"
        style["width"] = 260
        style["height"] = 120
        
        # Ajustar estilo según si está habilitada o no
        if enabled:
            style["bg"] = "white"
            cursor = "hand2"
        else:
            style["bg"] = "#f5f5f5"  # Gris claro para deshabilitado
            cursor = "arrow"
            color = "#999999"  # Gris para icono y texto deshabilitado
        
        card_frame = tk.Frame(parent, **style)
        card_frame.pack_propagate(False)
        card_frame.configure(cursor=cursor)
        
        # Contenido centrado
        content_frame = tk.Frame(card_frame, bg=style["bg"])
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icono grande
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=("Segoe UI", 32),
            fg=color,
            bg=style["bg"]
        )
        icon_label.pack(pady=(0, 6))
        
        # Título centrado y grande
        title_label = tk.Label(
            content_frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            fg=color,
            bg=style["bg"],
            anchor="center",
            justify="center"
        )
        title_label.pack(fill="x")
        
        # Si está deshabilitada, agregar mensaje de ayuda
        if not enabled and disabled_message:
            help_label = tk.Label(
                content_frame,
                text=disabled_message,
                font=("Segoe UI", 9),
                fg="#666666",
                bg=style["bg"],
                anchor="center",
                justify="center",
                wraplength=220
            )
            help_label.pack(pady=(4, 0))
        
        # Hover effect solo si está habilitada
        if enabled:
            def on_enter(e):
                card_frame.configure(bg="#e3f2fd")
                content_frame.configure(bg="#e3f2fd")
                icon_label.configure(bg="#e3f2fd")
                title_label.configure(bg="#e3f2fd")
                if not enabled and disabled_message:
                    help_label.configure(bg="#e3f2fd")
            
            def on_leave(e):
                card_frame.configure(bg="white")
                content_frame.configure(bg="white")
                icon_label.configure(bg="white")
                title_label.configure(bg="white")
                if not enabled and disabled_message:
                    help_label.configure(bg="white")
            
            card_frame.bind("<Enter>", on_enter)
            card_frame.bind("<Leave>", on_leave)
            
            for w in [content_frame, icon_label, title_label]:
                w.bind("<Button-1>", lambda e: action())
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.configure(cursor="hand2")
            
            # Click
            card_frame.bind("<Button-1>", lambda e: action())
        else:
            # Si está deshabilitada, mostrar tooltip al hacer hover
            def show_disabled_tooltip(e):
                if disabled_message:
                    # Crear tooltip temporal
                    tooltip = tk.Toplevel(card_frame)
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{e.x_root+10}+{e.y_root+10}")
                    
                    label = tk.Label(tooltip, text=disabled_message, 
                                   justify="left", background="#ffffe0", 
                                   relief="solid", borderwidth=1,
                                   font=("Segoe UI", 9))
                    label.pack()
                    
                    def hide_tooltip(e):
                        tooltip.destroy()
                    
                    tooltip.bind("<Leave>", hide_tooltip)
                    card_frame.bind("<Leave>", hide_tooltip)
            
            card_frame.bind("<Enter>", show_disabled_tooltip)
        
        return card_frame
    
    def _get_tenant_statistics(self):
        """Obtiene estadísticas de inquilinos"""
        from manager.app.services.tenant_service import tenant_service
        return tenant_service.get_statistics()
    
    def refresh_dashboard(self):
        """Refresca las estadísticas del dashboard"""
        # Solo refrescar si estamos en el dashboard
        current_view = getattr(self, '_current_view', None)
        if current_view == "dashboard":
            # Limpiar contenido actual
            for widget in self.views_container.winfo_children():
                widget.destroy()
            # Recrear la vista del dashboard
            self._create_dashboard_view()
    
    def refresh_tenants_view(self):
        """Refresca la vista de inquilinos para mostrar estados actualizados"""
        # SIEMPRE refrescar, sin importar desde dónde se llame
        current_view = getattr(self, '_current_view', None)
        print(f"🔄 Refrescando vista de inquilinos desde vista: {current_view}")
        
        try:
            # Forzar actualización de Tkinter antes de refrescar
            self.root.update_idletasks()
            self.root.update()
            
            # Limpiar contenido actual
            for widget in self.views_container.winfo_children():
                widget.destroy()
            
            # Forzar actualización después de limpiar
            self.root.update_idletasks()
            self.root.update()
            
            # Recrear la vista de inquilinos
            self._create_tenants_view()
            
            # Forzar actualización después de recrear
            self.root.update_idletasks()
            self.root.update()
            
            # Forzar actualización final
            self.root.after(100, self.root.update_idletasks)
            self.root.after(200, self.root.update)
            
            print(f"✅ Vista de inquilinos refrescada automáticamente (SIEMPRE)")
        except Exception as e:
            print(f"⚠️ Error al refrescar vista de inquilinos: {str(e)}")
    
    def _force_tenants_refresh(self):
        """Fuerza un refresh completo de la vista de inquilinos"""
        print(f"🔄 Forzando refresh completo de vista de inquilinos")
        try:
            # Limpiar contenido actual
            for widget in self.views_container.winfo_children():
                widget.destroy()
            
            # Recrear la vista de inquilinos
            self._create_tenants_view()
            
            # Forzar actualización múltiple
            self.root.update_idletasks()
            self.root.update()
            self.root.after(100, self.root.update_idletasks)
            self.root.after(200, self.root.update)
            
            print(f"✅ Refresh completo forzado exitosamente")
        except Exception as e:
            print(f"⚠️ Error al forzar refresh: {str(e)}")
    
    def _get_payments_of_current_month(self):
        from manager.app.services.payment_service import PaymentService
        import datetime
        service = PaymentService()
        now = datetime.datetime.now()
        pagos = service.get_all_payments()
        pagos_mes = [p for p in pagos if self._is_payment_in_current_month(p, now)]
        total = sum(float(p.get('monto', 0)) for p in pagos_mes)
        return total

    def _is_payment_in_current_month(self, pago, now):
        # fecha_pago formato 'DD/MM/YYYY'
        try:
            fecha = pago.get('fecha_pago', '')
            if not fecha:
                return False
            dia, mes, anio = map(int, fecha.split('/'))
            return mes == now.month and anio == now.year
        except Exception:
            return False
    
    def _show_register_payment_direct(self):
        """Navega a la vista de pagos y abre directamente el registro de pago"""
        # Limpiar contenido actual
        self._update_nav_buttons("payments")
        self.page_title.configure(text="Registrar pagos")
        for widget in self.views_container.winfo_children():
            widget.destroy()
        payments_view = PaymentsView(
            self.views_container, 
            on_back=lambda: self._navigate_to("dashboard"),
            on_payment_saved=self.refresh_tenants_view
        )
        payments_view.pack(fill="both", expand=True)
        payments_view._show_register_payment()
    
    def navigate_to_payments(self, tenant=None):
        """Navega a la vista de pagos y abre el formulario con el inquilino preseleccionado si se proporciona."""
        self._update_nav_buttons("payments")
        self.page_title.configure(text="Registrar pagos")
        for widget in self.views_container.winfo_children():
            widget.destroy()
        payments_view = PaymentsView(
            self.views_container, 
            on_back=lambda: self._navigate_to("dashboard"), 
            preselected_tenant=tenant,
            on_payment_saved=self.refresh_tenants_view
        )
        payments_view.pack(fill="both", expand=True)
        payments_view._show_register_payment(preselected_tenant=tenant)
    
    def _show_register_expense_direct(self):
        """Navega directamente al formulario de registrar gasto"""
        self._update_nav_buttons("expenses")
        self.page_title.configure(text="Registrar Gasto")
        for widget in self.views_container.winfo_children():
            widget.destroy()
        from .register_expense_view import RegisterExpenseView
        form = RegisterExpenseView(self.views_container, on_back=lambda: self._navigate_to("dashboard"))
        form.pack(fill="both", expand=True)
    
    def _show_building_setup_view(self):
        """Muestra el asistente de configuración del edificio."""
        self.page_title.configure(text="Configuración del Edificio")
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        setup_view = BuildingSetupView(self.views_container, on_back=lambda: self._navigate_to("administration"))
        setup_view.pack(fill="both", expand=True)

    def _show_building_management_view(self):
        """Muestra la vista para gestionar edificios existentes."""
        self.page_title.configure(text="Gestión de Edificios")
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        management_view = BuildingManagementView(self.views_container, on_back=lambda: self._navigate_to("administration"))
        management_view.pack(fill="both", expand=True)

    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop() 

    def _get_expenses_of_current_month(self):
        from manager.app.services.expense_service import ExpenseService
        import datetime
        service = ExpenseService()
        now = datetime.datetime.now()
        expenses = service.filter_expenses(year=now.year, month=now.month)
        total = sum(float(e.get('monto', 0)) for e in expenses)
        return total 