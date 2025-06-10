"""
Ventana principal profesional para Building Manager
Diseño moderno con navegación elegante
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from ..components.modern_widgets import ModernButton, ModernCard, ModernSeparator, ModernMetricCard, DetailedMetricCard

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
        # Actualizar estado de botones de navegación
        self._update_nav_buttons(view_name)
        
        # Actualizar título
        titles = {
            "dashboard": "Dashboard",
            "tenants": "Gestión de Inquilinos",
            "payments": "Control de Pagos",
            "expenses": "Gestión de Gastos",
            "reports": "Reportes y Análisis",
            "settings": "Configuración"
        }
        
        self.page_title.configure(text=titles.get(view_name, "Building Manager"))
        
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Cargar nueva vista
        self._load_view(view_name)
    
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
        elif view_name == "payments":
            self._create_placeholder_view("Módulo de Pagos", "Gestión de pagos y facturación")
        elif view_name == "expenses":
            self._create_placeholder_view("Módulo de Gastos", "Control de gastos y contabilidad")
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
            value="$2,450",
            icon=Icons.PAYMENT_PENDING,
            trend="-$300",
            color_theme="warning"
        )
        metric2.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Métrica 3: Ingresos del Mes
        metric3 = ModernMetricCard(
            metrics_row,
            title="Ingresos del Mes",
            value="$15,200",
            icon=Icons.PAYMENT_RECEIVED,
            trend="+8.5%",
            color_theme="success"
        )
        metric3.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Métrica 4: Gastos del Mes
        metric4 = ModernMetricCard(
            metrics_row,
            title="Gastos del Mes", 
            value="$3,100",
            icon=Icons.EXPENSES,
            trend="+$200",
            color_theme="error"
        )
        metric4.pack(side="left", fill="both", expand=True)
        
        # Separador elegante
        ModernSeparator(self.views_container)
        
        # Grid de acciones principales del administrador
        self._create_admin_actions_grid()
    
    def _create_tenants_view(self):
        """Crea la vista de inquilinos"""
        from .tenants_view import TenantsView
        
        tenants_view = TenantsView(
            self.views_container,
            on_navigate=self._navigate_to
        )
        tenants_view.pack(fill="both", expand=True)
    
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
        
        # Contenedor del grid con distribución uniforme
        grid_container = tk.Frame(main_container, **theme_manager.get_style("frame"))
        grid_container.pack(fill="both", expand=True)
        
        # Primera fila de cards
        row1 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row1.pack(fill="both", expand=True, pady=(0, Spacing.MD))
        
        # Card 1: Nuevo Inquilino
        self._create_admin_action_card(
            row1,
            "👤",
            "Nuevo Inquilino",
            "Registrar nuevo inquilino en el sistema",
            "#2563eb",  # Azul principal
            lambda: self._navigate_to("tenants")
        ).pack(side="left", fill="both", expand=True, padx=(0, Spacing.LG))
        
        # Card 2: Registrar Pago
        self._create_admin_action_card(
            row1,
            "💰",
            "Registrar Pago",
            "Registrar pago recibido de inquilino",
            "#059669",  # Verde éxito
            lambda: self._navigate_to("payments")
        ).pack(side="left", fill="both", expand=True, padx=(0, Spacing.LG))
        
        # Card 3: Registrar Gasto
        self._create_admin_action_card(
            row1,
            "💸",
            "Registrar Gasto",
            "Anotar gastos del edificio",
            "#dc2626",  # Rojo gastos
            lambda: self._navigate_to("expenses")
        ).pack(side="left", fill="both", expand=True)
        
        # Segunda fila de cards
        row2 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row2.pack(fill="both", expand=True)
        
        # Card 4: Buscar Inquilino
        self._create_admin_action_card(
            row2,
            "🔍",
            "Buscar Inquilino",
            "Búsqueda rápida por nombre",
            "#7c3aed",  # Púrpura búsqueda
            lambda: self._show_search_dialog()
        ).pack(side="left", fill="both", expand=True, padx=(0, Spacing.LG))
        
        # Card 5: Generar Reporte
        self._create_admin_action_card(
            row2,
            "📊",
            "Generar Reporte",
            "Reportes de inquilinos y finanzas",
            "#ea580c",  # Naranja reportes
            lambda: self._navigate_to("reports")
        ).pack(side="left", fill="both", expand=True, padx=(0, Spacing.LG))
        
        # Card 6: Pagos Pendientes
        self._create_admin_action_card(
            row2,
            "⏰",
            "Pagos Pendientes",
            "Lista de pagos por cobrar",
            "#d97706",  # Amarillo advertencia
            lambda: self._show_pending_payments()
        ).pack(side="left", fill="both", expand=True)
    
    def _create_admin_action_card(self, parent, icon, title, description, color, command):
        """Crea una card de acción para el administrador"""
        # Frame principal de la card que se adapta al espacio disponible
        card_frame = tk.Frame(
            parent,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            relief="solid",
            bd=1,
            highlightbackground=theme_manager.themes[theme_manager.current_theme]["border_light"],
            highlightthickness=1
        )
        
        # Contenido de la card centrado verticalmente
        content_frame = tk.Frame(card_frame, bg=card_frame["bg"])
        content_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        # Frame interno para centrar contenido verticalmente
        inner_frame = tk.Frame(content_frame, bg=card_frame["bg"])
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icono optimizado
        icon_label = tk.Label(
            inner_frame,
            text=icon,
            font=("Segoe UI", 26),
            bg=card_frame["bg"],
            fg=color
        )
        icon_label.pack(pady=(0, 3))
        
        # Título más legible
        title_label = tk.Label(
            inner_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=card_frame["bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        title_label.pack(pady=(0, 1))
        
        # Descripción completamente visible
        desc_label = tk.Label(
            inner_frame,
            text=description,
            font=("Segoe UI", 9),
            bg=card_frame["bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"],
            wraplength=260,
            justify="center"
        )
        desc_label.pack()
        
        # Efectos hover y click mejorados
        def on_enter(event):
            card_frame.configure(
                bg=color, 
                bd=2, 
                highlightbackground=color,
                relief="solid"
            )
            content_frame.configure(bg=color)
            inner_frame.configure(bg=color)
            for widget in [icon_label, title_label, desc_label]:
                widget.configure(bg=color, fg="white")
        
        def on_leave(event):
            original_bg = theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            card_frame.configure(
                bg=original_bg, 
                bd=1,
                highlightbackground=theme_manager.themes[theme_manager.current_theme]["border_light"],
                relief="solid"
            )
            content_frame.configure(bg=original_bg)
            inner_frame.configure(bg=original_bg)
            icon_label.configure(bg=original_bg, fg=color)
            title_label.configure(bg=original_bg, fg=theme_manager.themes[theme_manager.current_theme]["text_primary"])
            desc_label.configure(bg=original_bg, fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"])
        
        def on_click(event):
            command()
        
        # Bind eventos a todos los widgets
        for widget in [card_frame, content_frame, inner_frame, icon_label, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            widget.configure(cursor="hand2")
        
        return card_frame
    
    def _show_search_dialog(self):
        """Muestra diálogo de búsqueda de inquilinos"""
        # Por ahora navegar a inquilinos, luego se puede implementar un diálogo específico
        self._navigate_to("tenants")
    
    def _show_pending_payments(self):
        """Muestra vista de pagos pendientes"""
        # Por ahora navegar a pagos, luego se puede implementar una vista específica
        self._navigate_to("payments")
    
    def _get_tenant_statistics(self):
        """Obtiene estadísticas de inquilinos"""
        # Datos estáticos por ahora - se puede conectar con el servicio más tarde
        return {
            "total": 12,
            "al_dia": 8,
            "pendiente": 2,
            "moroso": 2
        }
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop() 