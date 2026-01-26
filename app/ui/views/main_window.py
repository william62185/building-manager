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
from .settings_view import SettingsView

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
                "active": False
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
        
        # Frame del botón - siempre usa bg_secondary (sin estado activo permanente)
        btn_frame = tk.Frame(
            parent,
            bg=theme["bg_secondary"],
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
            fg=theme["text_primary"],
            width=3
        )
        icon_label.pack(side="left")
        
        # Texto
        text_label = tk.Label(
            inner_frame,
            text=item["text"],
            font=("Segoe UI", 11, "normal"),
            bg=inner_frame.cget("bg"),
            fg=theme["text_primary"],
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True, padx=(Spacing.MD, 0))
        
        # Efectos de hover y click - todos los botones solo cambian en hover
        def on_click(event=None):
            item["command"]()
        
        def on_enter(event):
            hover_bg = theme["bg_tertiary"]
            btn_frame.configure(bg=hover_bg)
            inner_frame.configure(bg=hover_bg)
            icon_label.configure(bg=hover_bg)
            text_label.configure(bg=hover_bg)
        
        def on_leave(event):
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
            # Todos los botones usan el mismo color base (sin estado activo permanente)
            bg_color = theme["bg_secondary"]
            text_color = theme["text_primary"]
            
            # Actualizar frame principal
            btn_frame.configure(bg=bg_color)
            
            # Actualizar todos los widgets hijos
            for child in btn_frame.winfo_children():
                child.configure(bg=bg_color)
                for grandchild in child.winfo_children():
                    # Mantener el estilo normal (no bold) para todos
                    if isinstance(grandchild, tk.Label):
                        current_font = grandchild.cget("font")
                        if isinstance(current_font, tuple):
                            # Remover "bold" si existe
                            font_parts = list(current_font)
                            if len(font_parts) >= 3:
                                font_parts[2] = "normal"
                            elif len(font_parts) >= 2 and "bold" in str(current_font):
                                font_parts = [font_parts[0], font_parts[1], "normal"]
                        grandchild.configure(bg=bg_color, fg=text_color, font=("Segoe UI", 11, "normal"))
    
    def _load_view(self, view_name: str):
        """Carga una vista específica"""
        if view_name == "dashboard":
            self._create_dashboard_view()
        elif view_name == "tenants":
            # Recargar datos de inquilinos antes de crear la vista para asegurar datos actualizados
            from manager.app.services.tenant_service import tenant_service
            try:
                # Recargar datos desde archivo
                tenant_service._load_data()
                # Recalcular estados basándose en pagos recientes
                tenant_service.recalculate_all_payment_statuses()
                # Recargar datos después del recálculo
                tenant_service._load_data()
            except Exception as e:
                print(f"Error al recargar datos de inquilinos: {str(e)}")
            
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
            settings_view = SettingsView(self.views_container, on_back=lambda: self._navigate_to("dashboard"))
            settings_view.pack(fill="both", expand=True)
    
    def _create_dashboard_view(self):
        """Crea la vista del dashboard"""
        # Grid de métricas principales con espaciado compacto
        metrics_frame = tk.Frame(self.views_container, **theme_manager.get_style("frame"))
        metrics_frame.pack(fill="x", pady=(0, Spacing.XL))
        
        # Fila de métricas con espaciado compacto y profesional
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
        metric1.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))
        
        # Métrica 2: Pagos Pendientes
        metric2 = ModernMetricCard(
            metrics_row,
            title="Pagos Pendientes",
            value=f"${int(2450):,}",
            icon=Icons.PAYMENT_PENDING,
            color_theme="warning"
        )
        metric2.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))
        
        # Métrica 3: Ingresos del Mes (real)
        ingresos_mes = self._get_payments_of_current_month()
        metric3 = ModernMetricCard(
            metrics_row,
            title="Ingresos del Mes",
            value=f"${int(ingresos_mes):,}",
            icon=Icons.PAYMENT_RECEIVED,
            color_theme="success"
        )
        metric3.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))
        
        # Métrica 4: Gastos del Mes
        gastos_mes = self._get_expenses_of_current_month()
        metric4 = ModernMetricCard(
            metrics_row,
            title="Gastos del Mes", 
            value=f"${int(gastos_mes):,}",
            icon=Icons.EXPENSES,
            color_theme="error"
        )
        metric4.pack(side="left", fill="both", expand=True, padx=(0, Spacing.XS))
        
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
        """Crea la vista de inquilinos con datos actualizados"""
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
        
        # Header con botones de navegación
        header_frame = tk.Frame(admin_frame, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.XL)
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        
        # Agregar solo botón Dashboard (sin Volver porque es redundante)
        self._create_navigation_buttons(buttons_frame, lambda: self._navigate_to("dashboard"), show_back_button=False)

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
                "icon": "⚙️",
                "title": "Gestión de Usuarios",
                "color": "#6366f1",
                "action": lambda: self._show_placeholder_dialog("Gestión de Usuarios", "Funcionalidad en desarrollo"),
                "enabled": True
            }
        ]
        
        # Crear filas de 3 tarjetas cada una con tamaño uniforme usando grid
        num_columns = 3
        num_rows = (len(actions_grid) + num_columns - 1) // num_columns  # Calcular número de filas
        
        # Contenedor para el grid con distribución uniforme
        grid_container = tk.Frame(admin_frame, **theme_manager.get_style("frame"))
        grid_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        # Configurar el grid para distribución uniforme
        for col in range(num_columns):
            grid_container.grid_columnconfigure(col, weight=1, uniform="col")
        for row in range(num_rows):
            grid_container.grid_rowconfigure(row, weight=1, uniform="row")
        
        row_num = 0
        for i in range(0, len(actions_grid), num_columns):
            row_items = actions_grid[i:i+num_columns]
            for col, item in enumerate(row_items):
                card = self._create_admin_action_card(
                    grid_container, item["icon"], item["title"], item["color"], 
                    item["action"], item.get("enabled", True), item.get("disabled_message", "")
                )
                card.grid(row=row_num, column=col, sticky="nsew", padx=(0, Spacing.LG) if col < len(row_items) - 1 else 0, pady=(0, Spacing.LG) if row_num < num_rows - 1 else 0)
            row_num += 1

    def _create_placeholder_view(self, title: str, subtitle: str):
        """Crea una vista placeholder"""
        card = ModernCard(self.views_container)
        card.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.XL)
        
        # Contenedor interno
        content_frame = tk.Frame(card, **theme_manager.get_style("frame"))
        content_frame.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.XL)
        
        # Título
        title_label = tk.Label(
            content_frame,
            text=title,
            **theme_manager.get_style("label_title")
        )
        title_label.pack(pady=(0, Spacing.MD))
        
        # Subtítulo
        if subtitle:
            subtitle_label = tk.Label(
                content_frame,
                text=subtitle,
                **theme_manager.get_style("label_body")
            )
            subtitle_label.pack(pady=(0, Spacing.LG))
        
        # Mensaje placeholder
        placeholder_label = tk.Label(
            content_frame,
            text="Modulo en desarrollo\n\nEste modulo sera implementado proximamente.",
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
                padx=Spacing.SM,
                pady=Spacing.SM
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
            on_save_success=self.refresh_dashboard,  # Callback para actualizar dashboard
            on_navigate_to_dashboard=lambda: self._navigate_to("dashboard")  # Callback directo para navegar al dashboard
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
            on_success=self._on_tenant_deactivated,
            on_navigate=self._navigate_to
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
        # Refrescar la vista de inquilinos si está activa
        self.refresh_tenants_view()
        # Volver a administración
        self._navigate_to("administration")

    def _create_admin_action_card(self, parent, icon: str, title: str, color: str, action: Callable, enabled: bool = True, disabled_message: str = ""):
        """Crea una card de acción administrativa mejorada visualmente"""
        theme = theme_manager.themes[theme_manager.current_theme]
        style = theme_manager.get_style("card").copy()
        style["bd"] = 1
        style["relief"] = "flat"
        style["highlightbackground"] = theme["border_light"]
        style["highlightthickness"] = 1
        # Establecer tamaño mínimo para uniformidad, pero permitir que grid estire
        # style["width"] = 400
        # style["height"] = 220
        
        # Ajustar estilo según si está habilitada o no
        if enabled:
            style["bg"] = "white"
            cursor = "hand2"
        else:
            style["bg"] = "#f5f5f5"  # Gris claro para deshabilitado
            cursor = "arrow"
            color = "#999999"  # Gris para icono y texto deshabilitado
        
        card_frame = tk.Frame(parent, **style)
        card_frame.configure(width=300, height=200)
        card_frame.pack_propagate(False)  # Mantener tamaño mínimo
        card_frame.configure(cursor=cursor)
        
        # Contenedor interno centrado con padding adecuado
        inner_container = tk.Frame(card_frame, bg=style["bg"])
        inner_container.pack(fill="both", expand=True)
        
        # Usar place para centrar el contenido verticalmente
        content_wrapper = tk.Frame(inner_container, bg=style["bg"])
        content_wrapper.place(relx=0.5, rely=0.5, anchor="center")
        
        # Sección superior para el icono con padding reducido
        icon_frame = tk.Frame(content_wrapper, bg=style["bg"])
        icon_frame.pack(pady=(0, Spacing.SM))
        
        # Icono grande y bien proporcionado
        icon_label = tk.Label(
            icon_frame,
            text=icon,
            font=("Segoe UI Symbol", 42),
            fg=color,
            bg=style["bg"]
        )
        icon_label.pack()
        
        # Sección inferior para el título
        title_frame = tk.Frame(content_wrapper, bg=style["bg"])
        title_frame.pack(fill="x", padx=Spacing.MD)
        
        # Título centrado y legible
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 15, "bold"),
            fg=color,
            bg=style["bg"],
            anchor="center",
            justify="center",
            wraplength=300
        )
        title_label.pack()
        
        # Si está deshabilitada, agregar mensaje de ayuda
        if not enabled and disabled_message:
            help_label = tk.Label(
                content_wrapper,
                text=disabled_message,
                font=("Segoe UI", 9),
                fg="#666666",
                bg=style["bg"],
                anchor="center",
                justify="center",
                wraplength=300
            )
            help_label.pack(pady=(Spacing.SM, 0))
        
        # Hover effect solo si está habilitada
        if enabled:
            def on_enter(e):
                hover_bg = "#f0f9ff"
                card_frame.configure(bg=hover_bg)
                inner_container.configure(bg=hover_bg)
                content_wrapper.configure(bg=hover_bg)
                icon_frame.configure(bg=hover_bg)
                title_frame.configure(bg=hover_bg)
                icon_label.configure(bg=hover_bg)
                title_label.configure(bg=hover_bg)
            
            def on_leave(e):
                original_bg = style["bg"]
                card_frame.configure(bg=original_bg)
                inner_container.configure(bg=original_bg)
                content_wrapper.configure(bg=original_bg)
                icon_frame.configure(bg=original_bg)
                title_frame.configure(bg=original_bg)
                icon_label.configure(bg=original_bg)
                title_label.configure(bg=original_bg)
            
            card_frame.bind("<Enter>", on_enter)
            card_frame.bind("<Leave>", on_leave)
            
            for w in [inner_container, content_wrapper, icon_frame, title_frame, icon_label, title_label]:
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
    
    def _create_navigation_buttons(self, parent, on_back_command, show_back_button=True):
        """Crea los botones Volver y Dashboard con estilo consistente"""
        from manager.app.ui.components.icons import Icons
        
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
        # Configuración común para ambos botones (misma altura)
        button_config = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": theme["btn_secondary_bg"],
            "fg": theme["btn_secondary_fg"],
            "activebackground": hover_bg,
            "activeforeground": theme["btn_secondary_fg"],
            "bd": 1,
            "relief": "solid",
            "padx": 12,
            "pady": 5,
            "cursor": "hand2"
        }
        
        # Botón "Volver" (solo si show_back_button es True)
        if show_back_button:
            btn_back = tk.Button(
                parent,
                text=f"{Icons.ARROW_LEFT} Volver",
                **button_config,
                command=on_back_command
            )
            btn_back.pack(side="right", padx=(Spacing.SM, 0))
            
            # Hover effect para botón "Volver"
            def on_enter_back(e):
                btn_back.configure(bg=hover_bg)
            
            def on_leave_back(e):
                btn_back.configure(bg=theme["btn_secondary_bg"])
            
            btn_back.bind("<Enter>", on_enter_back)
            btn_back.bind("<Leave>", on_leave_back)
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard)
        btn_dashboard = tk.Button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            **button_config,
            command=lambda: self._navigate_to("dashboard")
        )
        btn_dashboard.pack(side="right")
        
        # Hover effect para botón "Dashboard"
        def on_enter_dashboard(e):
            btn_dashboard.configure(bg=hover_bg)
        
        def on_leave_dashboard(e):
            btn_dashboard.configure(bg=theme["btn_secondary_bg"])
        
        btn_dashboard.bind("<Enter>", on_enter_dashboard)
        btn_dashboard.bind("<Leave>", on_leave_dashboard)
    
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
        """Refresca la vista de inquilinos para mostrar estados actualizados en tiempo real"""
        current_view = getattr(self, '_current_view', None)
        print(f"🔄 Refrescando vista de inquilinos desde vista: {current_view}")
        
        try:
            # Primero intentar refrescar si la vista de inquilinos ya está activa
            if current_view == "tenants":
                # Buscar la instancia de TenantsView en los widgets hijos
                for widget in self.views_container.winfo_children():
                    if isinstance(widget, TenantsView):
                        # Si está en la lista, refrescar solo la lista sin destruir la vista
                        if widget.current_view == "list":
                            widget.refresh_list()
                            print("✅ Lista de inquilinos refrescada en tiempo real (sin recrear vista)")
                            # Forzar actualización de la UI
                            self.root.update_idletasks()
                            self.root.update()
                            return
                        # Si está en otra subvista (dashboard, details), refrescar cuando vuelva a lista
            
            # Si no estamos en la vista de inquilinos o no está en lista, 
            # los datos se recargarán automáticamente cuando navegues a inquilinos
            # gracias a _create_tenants_view() que ya recarga datos
            
            print(f"✅ Callback de refresh ejecutado - Los datos se actualizarán al navegar a inquilinos")
        except Exception as e:
            print(f"⚠️ Error al refrescar vista de inquilinos: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _force_tenants_refresh(self):
        """Fuerza un refresh completo de la vista de inquilinos"""
        print("Forzando refresh completo de vista de inquilinos")
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
            
            print(f"Refresh completo forzado exitosamente")
        except Exception as e:
            print(f"Error al forzar refresh: {str(e)}")
    
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
        form = RegisterExpenseView(
            self.views_container, 
            on_back=lambda: self._navigate_to("dashboard"),
            on_navigate_to_dashboard=lambda: self._navigate_to("dashboard")
        )
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