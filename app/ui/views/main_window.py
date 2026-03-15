"""
Ventana principal profesional para Building Manager
Diseño moderno con navegación elegante
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable
from tkinter import messagebox
from datetime import datetime, timedelta
import os
import subprocess
from pathlib import Path
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard, ModernSeparator, ModernMetricCard, DetailedMetricCard, create_rounded_button, get_module_colors
from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service
from manager.app.services.expense_service import ExpenseService
from manager.app.logger import logger
from .payments_view import PaymentsView
from .tenants_view import TenantsView
from .expenses_view import ExpensesView
from .apartment_management_view import ApartmentManagementView
from .building_setup_view import BuildingSetupView
from .apartment_form_view import ApartmentFormView
from .apartments_list_view import ApartmentsListView
from .building_management_view import BuildingManagementView
from .settings_view import SettingsView
from .reports_view import ReportsView
from .reports.occupancy_vacancy_report_view import OccupancyVacancyReportView
from .backup_view import BackupView
from .user_management_view import UserManagementView
from .dashboard_view import DashboardView
from .pending_payments_report_window import show_pending_payments_report
from manager.app.app_controller import AppController
from manager.app.presenters.dashboard_presenter import DashboardPresenter
from manager.app.presenters.report_presenter import ReportPresenter

class MainWindow:
    """Ventana principal con diseño profesional"""

    def __init__(self, root=None, current_user=None):
        self._owns_root = root is None
        self.root = root if root is not None else tk.Tk()
        self.current_view = None
        self.views = {}

        from manager.app.services.user_service import user_service
        self.user_service = user_service
        self.current_user = current_user if current_user is not None else self._get_current_user()
        if self.current_user and "password_hash" in self.current_user:
            self.current_user = {k: v for k, v in self.current_user.items() if k != "password_hash"}

        self._setup_window()
        self.app_controller = AppController(self)
        self._dashboard_presenter = DashboardPresenter()
        self._report_presenter = ReportPresenter()
        self._create_layout()
        if not self._owns_root:
            # Primero revisar licencia/demo y luego mostrar onboarding.
            self.root.after(150, self._check_license_status)
            self.root.after(350, self._maybe_show_onboarding)
    
    def _get_current_user(self):
        """Obtiene el usuario actual del sistema (fallback cuando no se pasa desde login)."""
        user = self.user_service.get_user_by_username("admin")
        if not user:
            self.user_service._create_default_admin()
            user = self.user_service.get_user_by_username("admin")
        if user:
            return {k: v for k, v in user.items() if k != "password_hash"}
        return None
        
    def _setup_window(self):
        """Configura la ventana principal"""
        self.root.title("Building Manager Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Maximizar la ventana al inicio
        self.root.state('zoomed')  # Windows
        # Para macOS y Linux sería: self.root.attributes('-zoomed', True)
        
        # Cargar tema desde configuración y aplicar
        try:
            from manager.app.services.app_config_service import app_config_service
            saved_theme = app_config_service.get_theme()
            if saved_theme in ["light", "dark"]:
                theme_manager.set_theme(saved_theme)
        except Exception:
            pass
        
        # Configurar estilos
        self.root.configure(**theme_manager.get_style("window"))
        
        # Icono de la aplicación (ruta vía paths_config para dev y frozen)
        try:
            from manager.app.paths_config import get_icon_path
            icon_path = get_icon_path()
            if icon_path:
                self.root.iconbitmap(str(icon_path))
        except Exception:
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
        # Frame principal (sin borde ni línea de resalte entre sidebar y contenido)
        main_frame = tk.Frame(self.root, **theme_manager.get_style("frame"), highlightthickness=0, bd=0)
        main_frame.pack(fill="both", expand=True)
        
        # Sidebar primero (reserva espacio a la izquierda)
        self._create_sidebar(main_frame)
        # Frame de 1px con el mismo color del sidebar para tapar la línea gris que Tk dibuja en el borde
        self._create_sidebar_edge_frame(main_frame)
        self._create_content_area(main_frame)
        
        # Cargar vista inicial
        self._navigate_to("dashboard")
    
    def _create_sidebar(self, parent):
        """Crea la barra lateral de navegación"""
        theme = theme_manager.themes[theme_manager.current_theme]
        self.sidebar_bg = theme.get("sidebar_bg", "#334155")  # combinación armónica con content_bg
        self.sidebar = tk.Frame(
            parent,
            width=280,
            bg=self.sidebar_bg,
            relief="flat",
            bd=0,
            highlightthickness=0
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
    
    def _create_sidebar_edge_frame(self, parent):
        """Frame con el color del sidebar para tapar la línea gris que Tk/Windows dibuja en el borde (varios px de ancho)."""
        self.sidebar_edge_frame = tk.Frame(
            parent,
            width=6,
            bg=self.sidebar_bg,
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.sidebar_edge_frame.pack(side="left", fill="y")
        self.sidebar_edge_frame.pack_propagate(False)
    
    def _create_sidebar_header(self):
        """Crea el header del sidebar con logo y título"""
        header_frame = tk.Frame(
            self.sidebar,
            bg=self.sidebar_bg,
            height=80
        )
        header_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        header_frame.pack_propagate(False)
        
        # Logo/Icono de la aplicación
        logo_frame = tk.Frame(header_frame, bg=header_frame.cget("bg"))
        logo_frame.pack(side="left")
        
        theme = theme_manager.themes[theme_manager.current_theme]
        sidebar_fg = theme.get("sidebar_fg", theme["text_primary"])
        sidebar_fg_sec = theme.get("sidebar_fg_secondary", theme["text_secondary"])
        logo_label = tk.Label(
            logo_frame,
            text="🏢",
            font=("Segoe UI Symbol", 28),
            bg=header_frame.cget("bg"),
            fg=sidebar_fg
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
            fg=sidebar_fg,
            anchor="w",
            justify="left"
        )
        title_label.pack(anchor="w")
        
        version_label = tk.Label(
            title_frame,
            text="v1.0 Pro",
            font=("Segoe UI", 9),
            bg=header_frame.cget("bg"),
            fg=sidebar_fg_sec,
            anchor="w"
        )
        version_label.pack(anchor="w")
    
    def _create_navigation_menu(self):
        """Crea el menú de navegación principal"""
        nav_frame = tk.Frame(
            self.sidebar,
            bg=self.sidebar_bg
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
        nav_bg = theme.get("sidebar_bg", theme["bg_secondary"])
        nav_fg = theme.get("sidebar_fg", theme["text_primary"])
        
        # Frame del botón - usa color del sidebar para coherencia (sin anillo de foco)
        btn_frame = tk.Frame(
            parent,
            bg=nav_bg,
            relief="flat",
            height=50,
            highlightthickness=0,
            highlightbackground=nav_bg,
            highlightcolor=nav_bg
        )
        btn_frame.pack(fill="x", pady=(0, Spacing.XS))
        btn_frame.pack_propagate(False)
        
        # Contenedor interno con padding (sin anillo de foco)
        inner_frame = tk.Frame(
            btn_frame,
            bg=btn_frame.cget("bg"),
            highlightthickness=0,
            highlightbackground=nav_bg,
            highlightcolor=nav_bg
        )
        inner_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Icono
        icon_label = tk.Label(
            inner_frame,
            text=item["icon"],
            font=("Segoe UI Symbol", 16),
            bg=inner_frame.cget("bg"),
            fg=nav_fg,
            width=3
        )
        icon_label.pack(side="left")
        
        # Texto
        text_label = tk.Label(
            inner_frame,
            text=item["text"],
            font=("Segoe UI", 11, "bold"),
            bg=inner_frame.cget("bg"),
            fg=nav_fg,
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True, padx=(Spacing.MD, 0))
        
        # Almacenar referencias a los widgets para poder actualizarlos después
        btn_frame.icon_label = icon_label
        btn_frame.text_label = text_label
        btn_frame.inner_frame = inner_frame
        btn_frame.button_name = item["text"].lower()  # Almacenar nombre para verificar estado activo
        
        # Efectos de hover y click - todos los botones solo cambian en hover
        def on_click(event=None):
            item["command"]()
        
        def on_enter(event):
            # Usar tema actual por si cambió (light/dark)
            # Azul para Inquilinos, Verde para Pagos, Rojo para Gastos, Morado para Administración, Naranja para Reportes
            t = theme_manager.themes[theme_manager.current_theme]
            if btn_frame.button_name == "inquilinos":
                # Azul para módulo de inquilinos en hover
                if theme_manager.current_theme == "dark":
                    hover_bg = "#1e3a5f"  # azul oscuro para modo oscuro
                    hover_fg = "#93c5fd"  # azul claro para modo oscuro
                else:
                    hover_bg = "#dbeafe"  # blue-100 - azul claro para fondo
                    hover_fg = "#1e40af"  # blue-800 - azul oscuro para texto
            elif btn_frame.button_name == "pagos":
                # Verde para módulo de pagos en hover
                if theme_manager.current_theme == "dark":
                    hover_bg = "#1e3a1e"  # verde oscuro para modo oscuro
                    hover_fg = "#4ade80"  # verde claro para modo oscuro
                else:
                    hover_bg = "#dcfce7"  # green-100 - verde claro para fondo
                    hover_fg = "#166534"  # green-800 - verde oscuro para texto
            elif btn_frame.button_name == "gastos":
                # Rojo para módulo de gastos en hover
                if theme_manager.current_theme == "dark":
                    hover_bg = "#7f1d1d"  # rojo oscuro para modo oscuro
                    hover_fg = "#fca5a5"  # rojo claro para modo oscuro
                else:
                    hover_bg = "#fee2e2"  # red-100 - rojo claro para fondo
                    hover_fg = "#991b1b"  # red-800 - rojo oscuro para texto
            elif btn_frame.button_name == "administración":
                # Morado para módulo de administración en hover
                if theme_manager.current_theme == "dark":
                    hover_bg = "#581c87"  # purple-800 - morado oscuro para modo oscuro
                    hover_fg = "#c084fc"  # purple-300 - morado claro para modo oscuro
                else:
                    hover_bg = "#f3e8ff"  # purple-100 - morado claro para fondo
                    hover_fg = "#7c3aed"  # purple-600 - morado oscuro para texto
            elif btn_frame.button_name == "reportes":
                # Naranja para módulo de reportes en hover
                if theme_manager.current_theme == "dark":
                    hover_bg = "#7c2d12"  # orange-900 - naranja oscuro para modo oscuro
                    hover_fg = "#fdba74"  # orange-300 - naranja claro para modo oscuro
                else:
                    hover_bg = "#ffedd5"  # orange-100 - naranja claro para fondo
                    hover_fg = "#c2410c"  # orange-800 - naranja oscuro para texto
            else:
                # Dashboard y Configuración: mismo hover que Inquilinos (no el del botón de usuario)
                if theme_manager.current_theme == "dark":
                    hover_bg = "#1e3a5f"  # azul oscuro para modo oscuro
                    hover_fg = "#93c5fd"  # azul claro para modo oscuro
                else:
                    hover_bg = "#dbeafe"  # blue-100 - azul claro para fondo
                    hover_fg = "#1e40af"  # blue-800 - azul oscuro para texto
            btn_frame.configure(bg=hover_bg)
            inner_frame.configure(bg=hover_bg)
            icon_label.configure(bg=hover_bg, fg=hover_fg)
            text_label.configure(bg=hover_bg, fg=hover_fg)
        
        def on_leave(event):
            # Solo resetear si el puntero salió del botón por completo.
            # Al pasar entre icono y texto se dispara Leave en uno y Enter en otro;
            # si reseteamos aquí, el color queda "pegado" o parpadea.
            try:
                root = btn_frame.winfo_toplevel()
                root.update_idletasks()
                px = root.winfo_pointerx()
                py = root.winfo_pointery()
                w = root.winfo_containing(px, py)
            except (tk.TclError, AttributeError):
                w = None
            # Sigue sobre el botón o algún hijo?
            if w is not None:
                cur = w
                while cur:
                    if cur == btn_frame:
                        return
                    try:
                        cur = cur.master
                    except (tk.TclError, AttributeError):
                        break
            
            # Verificar si este botón está activo antes de resetear
            # Si está activo, mantener el estilo activo en lugar del normal
            current_view = getattr(self, '_current_view', None)
            view_to_button = {
                "dashboard": "dashboard",
                "tenants": "inquilinos",
                "payments": "pagos",
                "expenses": "gastos",
                "administration": "administración",
                "reports": "reportes",
                "settings": "configuración"
            }
            active_button_name = view_to_button.get(current_view, "").lower()
            is_active = btn_frame.button_name == active_button_name
            
            if is_active:
                # Mantener estilo activo - Azul para Inquilinos, Verde para Pagos, Rojo para Gastos, Morado para Administración, Naranja para Reportes
                t = theme_manager.themes[theme_manager.current_theme]
                if btn_frame.button_name == "inquilinos":
                    # Azul para módulo de inquilinos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#1e3a5f"  # azul oscuro para modo oscuro
                        active_fg = "#93c5fd"  # azul claro para modo oscuro
                    else:
                        active_bg = "#dbeafe"  # blue-100 - azul claro para fondo
                        active_fg = "#1e40af"  # blue-800 - azul oscuro para texto
                elif btn_frame.button_name == "pagos":
                    # Verde para módulo de pagos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#1e3a1e"  # verde oscuro para modo oscuro
                        active_fg = "#4ade80"  # verde claro para modo oscuro
                    else:
                        active_bg = "#dcfce7"  # green-100 - verde claro para fondo
                        active_fg = "#166534"  # green-800 - verde oscuro para texto
                elif btn_frame.button_name == "gastos":
                    # Rojo para módulo de gastos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#7f1d1d"  # rojo oscuro para modo oscuro
                        active_fg = "#fca5a5"  # rojo claro para modo oscuro
                    else:
                        active_bg = "#fee2e2"  # red-100 - rojo claro para fondo
                        active_fg = "#991b1b"  # red-800 - rojo oscuro para texto
                elif btn_frame.button_name == "administración":
                    # Morado para módulo de administración
                    if theme_manager.current_theme == "dark":
                        active_bg = "#581c87"  # purple-800 - morado oscuro para modo oscuro
                        active_fg = "#c084fc"  # purple-300 - morado claro para modo oscuro
                    else:
                        active_bg = "#f3e8ff"  # purple-100 - morado claro para fondo
                        active_fg = "#7c3aed"  # purple-600 - morado oscuro para texto
                elif btn_frame.button_name == "reportes":
                    # Naranja para módulo de reportes
                    if theme_manager.current_theme == "dark":
                        active_bg = "#7c2d12"  # orange-900 - naranja oscuro para modo oscuro
                        active_fg = "#fdba74"  # orange-300 - naranja claro para modo oscuro
                    else:
                        active_bg = "#ffedd5"  # orange-100 - naranja claro para fondo
                        active_fg = "#c2410c"  # orange-800 - naranja oscuro para texto
                else:
                    # Dashboard y Configuración: mismo estilo activo que Inquilinos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#1e3a5f"  # azul oscuro para modo oscuro
                        active_fg = "#93c5fd"  # azul claro para modo oscuro
                    else:
                        active_bg = "#dbeafe"  # blue-100 - azul claro para fondo
                        active_fg = "#1e40af"  # blue-800 - azul oscuro para texto
                btn_frame.configure(bg=active_bg)
                inner_frame.configure(bg=active_bg)
                icon_label.configure(bg=active_bg, fg=active_fg)
                text_label.configure(bg=active_bg, fg=active_fg, font=("Segoe UI", 11, "bold"))
            else:
                # Resetear a estilo normal (color del sidebar)
                t = theme_manager.themes[theme_manager.current_theme]
                orig_bg = t.get("sidebar_bg", t["bg_secondary"])
                orig_fg = t.get("sidebar_fg", t["text_primary"])
                btn_frame.configure(bg=orig_bg)
                inner_frame.configure(bg=orig_bg)
                icon_label.configure(bg=orig_bg, fg=orig_fg)
                text_label.configure(bg=orig_bg, fg=orig_fg, font=("Segoe UI", 11, "bold"))
        
        # Bind events
        for widget in [btn_frame, inner_frame, icon_label, text_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        
        return btn_frame
    
    def _update_sidebar_theme(self, theme_name: str = None):
        """Actualiza los colores del sidebar cuando cambia el tema"""
        if theme_name is None:
            theme_name = theme_manager.current_theme
        
        if theme_name not in theme_manager.themes:
            return
        
        try:
            if not hasattr(self, 'sidebar') or not self.sidebar.winfo_exists():
                return
            
            theme = theme_manager.themes[theme_name]
            sidebar_color = theme.get("sidebar_bg", theme["bg_secondary"])
            content_color = theme.get("content_bg", getattr(self, "content_bg", "#f1f5f9"))
            
            # Actualizar fondo del sidebar
            self.sidebar.configure(bg=sidebar_color)
            self.sidebar_bg = sidebar_color
            # Mantener frame de borde y overlay del borde del contenido con el color del sidebar
            if hasattr(self, 'sidebar_edge_frame') and self.sidebar_edge_frame.winfo_exists():
                self.sidebar_edge_frame.configure(bg=sidebar_color)
            if hasattr(self, 'content_edge_overlay') and self.content_edge_overlay.winfo_exists():
                self.content_edge_overlay.configure(bg=sidebar_color)
            # Actualizar área de contenido para que mantenga la combinación con el sidebar
            self.content_bg = content_color
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                self.content_frame.configure(bg=content_color)
            if hasattr(self, 'views_container') and self.views_container.winfo_exists():
                self.views_container.configure(bg=content_color)
            # Actualizar barra del título (header)
            header_color = theme.get("header_bg", getattr(self, "header_bg", "#e84118"))
            self.header_bg = header_color
            if hasattr(self, 'content_header_frame') and self.content_header_frame.winfo_exists():
                self.content_header_frame.configure(bg=header_color)
            if hasattr(self, 'page_title_canvas') and self.page_title_canvas.winfo_exists():
                self.page_title_canvas.configure(bg=header_color)
                self._draw_page_title()
            
            # Actualizar todos los frames hijos del sidebar (sidebar_bg + texto claro)
            self._update_widget_theme_recursive(self.sidebar, theme, "sidebar_bg", "sidebar_fg", "sidebar_fg_secondary")
            
            # Actualizar botones de navegación
            if hasattr(self, 'nav_buttons'):
                for btn_name, btn_frame in self.nav_buttons.items():
                    if btn_frame.winfo_exists():
                        self._update_nav_button_theme(btn_frame, theme)
            
        except Exception as e:
            logger.exception("Error al actualizar tema del sidebar: %s", e)
    
    def _update_widget_theme_recursive(self, widget, theme, bg_key, fg_key, fg_secondary_key):
        """Actualiza recursivamente los colores de los widgets"""
        try:
            if not widget.winfo_exists():
                return
            
            widget_type = widget.winfo_class()
            current_bg = widget.cget("bg")
            current_fg = widget.cget("fg")
            
            # Colores de tema para comparación (incl. paleta complementaria navy/orange-50)
            light_bg_colors = ["#f9fafb", "#ffffff", "#f3f4f6", "#f8fafc", "#f1f5f9", "#e2e8f0", "#f4f4e0", "#fce7e5", "#e0dab8", "#d0ca98", "#e8c4b8", "#d49888", "#b86a5c", "#e5e7eb", "#dbeafe", "#bfdbfe", "#bbf7d0", "#fecaca", "#e9d5ff", "#fed7aa", "#fff7ed", "#1e3a5f", "#2563eb"]
            dark_bg_colors = ["#111827", "#1f2937", "#334155", "#374151", "#4b5563"]
            light_fg_colors = ["#1f2937", "#6b7280", "#9ca3af", "#ffffff", "#94a3b8"]
            dark_fg_colors = ["#f9fafb", "#d1d5db", "#9ca3af"]
            
            # Actualizar frames
            if widget_type in ["Frame", "Toplevel"]:
                # Solo actualizar si es un color de tema
                if current_bg in light_bg_colors or current_bg in dark_bg_colors:
                    widget.configure(bg=theme[bg_key])
                # También actualizar separadores (frames con altura 1)
                elif widget.cget("height") == "1" or widget.cget("height") == 1:
                    # Es un separador, usar border_light
                    widget.configure(bg=theme["border_light"])
            
            # Actualizar labels
            elif widget_type == "Label":
                # Actualizar fondo si es un color de tema
                if current_bg in light_bg_colors or current_bg in dark_bg_colors:
                    widget.configure(bg=theme[bg_key])
                
                if current_fg in light_fg_colors or current_fg in dark_fg_colors:
                    if current_fg in ["#1f2937", "#f9fafb", "#ffffff"]:
                        widget.configure(fg=theme[fg_key])
                    elif current_fg in ["#6b7280", "#d1d5db", "#9ca3af", "#e8e4f5", "#94a3b8"]:
                        widget.configure(fg=theme[fg_secondary_key])
                    elif current_fg in ["#2563eb", "#60a5fa"]:
                        widget.configure(fg=theme["text_accent"])
            
            # Actualizar recursivamente los hijos
            for child in widget.winfo_children():
                self._update_widget_theme_recursive(child, theme, bg_key, fg_key, fg_secondary_key)
                
        except (tk.TclError, AttributeError):
            pass
    
    def _update_nav_button_theme(self, btn_frame, theme):
        """Actualiza los colores de un botón de navegación"""
        try:
            if not btn_frame.winfo_exists():
                return
            
            # Verificar si este botón está activo
            current_view = getattr(self, '_current_view', None)
            view_to_button = {
                "dashboard": "dashboard",
                "tenants": "inquilinos",
                "payments": "pagos",
                "expenses": "gastos",
                "administration": "administración",
                "reports": "reportes",
                "settings": "configuración"
            }
            active_button_name = view_to_button.get(current_view, "").lower()
            button_name = getattr(btn_frame, 'button_name', '').lower()
            is_active = button_name == active_button_name
            
            if is_active:
                # Aplicar estilo activo - Azul para Inquilinos, Verde para Pagos, Rojo para Gastos, Morado para Administración, Naranja para Reportes
                if button_name == "inquilinos":
                    # Azul para módulo de inquilinos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#1e3a5f"  # azul oscuro para modo oscuro
                        active_fg = "#93c5fd"  # azul claro para modo oscuro
                    else:
                        active_bg = "#dbeafe"  # blue-100 - azul claro para fondo
                        active_fg = "#1e40af"  # blue-800 - azul oscuro para texto
                elif button_name == "pagos":
                    # Verde para módulo de pagos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#1e3a1e"  # verde oscuro para modo oscuro
                        active_fg = "#4ade80"  # verde claro para modo oscuro
                    else:
                        active_bg = "#dcfce7"  # green-100 - verde claro para fondo
                        active_fg = "#166534"  # green-800 - verde oscuro para texto
                elif button_name == "gastos":
                    # Rojo para módulo de gastos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#7f1d1d"  # rojo oscuro para modo oscuro
                        active_fg = "#fca5a5"  # rojo claro para modo oscuro
                    else:
                        active_bg = "#fee2e2"  # red-100 - rojo claro para fondo
                        active_fg = "#991b1b"  # red-800 - rojo oscuro para texto
                elif button_name == "administración":
                    # Morado para módulo de administración
                    if theme_manager.current_theme == "dark":
                        active_bg = "#581c87"  # purple-800 - morado oscuro para modo oscuro
                        active_fg = "#c084fc"  # purple-300 - morado claro para modo oscuro
                    else:
                        active_bg = "#f3e8ff"  # purple-100 - morado claro para fondo
                        active_fg = "#7c3aed"  # purple-600 - morado oscuro para texto
                elif button_name == "reportes":
                    # Naranja para módulo de reportes
                    if theme_manager.current_theme == "dark":
                        active_bg = "#7c2d12"  # orange-900 - naranja oscuro para modo oscuro
                        active_fg = "#fdba74"  # orange-300 - naranja claro para modo oscuro
                    else:
                        active_bg = "#ffedd5"  # orange-100 - naranja claro para fondo
                        active_fg = "#c2410c"  # orange-800 - naranja oscuro para texto
                else:
                    # Dashboard y Configuración: mismo estilo activo que Inquilinos
                    if theme_manager.current_theme == "dark":
                        active_bg = "#1e3a5f"
                        active_fg = "#93c5fd"
                    else:
                        active_bg = "#dbeafe"
                        active_fg = "#1e40af"
                
                btn_frame.configure(bg=active_bg)
                
                if hasattr(btn_frame, 'inner_frame') and btn_frame.inner_frame.winfo_exists():
                    btn_frame.inner_frame.configure(bg=active_bg)
                else:
                    for child in btn_frame.winfo_children():
                        if child.winfo_class() == "Frame":
                            child.configure(bg=active_bg)
                
                if hasattr(btn_frame, 'icon_label') and btn_frame.icon_label.winfo_exists():
                    btn_frame.icon_label.configure(bg=active_bg, fg=active_fg)
                if hasattr(btn_frame, 'text_label') and btn_frame.text_label.winfo_exists():
                    btn_frame.text_label.configure(bg=active_bg, fg=active_fg, font=("Segoe UI", 11, "bold"))
            else:
                # Aplicar estilo normal (usar sidebar_bg para que coincida con el menú)
                nav_bg = theme.get("sidebar_bg", theme["bg_secondary"])
                btn_frame.configure(bg=nav_bg)
                
                if hasattr(btn_frame, 'inner_frame') and btn_frame.inner_frame.winfo_exists():
                    btn_frame.inner_frame.configure(bg=nav_bg)
                else:
                    for child in btn_frame.winfo_children():
                        if child.winfo_class() == "Frame":
                            child.configure(bg=nav_bg)
                
                nav_fg = theme.get("sidebar_fg", theme["text_primary"])
                if hasattr(btn_frame, 'icon_label') and btn_frame.icon_label.winfo_exists():
                    btn_frame.icon_label.configure(bg=nav_bg, fg=nav_fg)
                if hasattr(btn_frame, 'text_label') and btn_frame.text_label.winfo_exists():
                    btn_frame.text_label.configure(bg=nav_bg, fg=nav_fg, font=("Segoe UI", 11, "bold"))
        except (tk.TclError, AttributeError):
            pass
    
    def _create_sidebar_footer(self):
        """Crea el footer del sidebar"""
        footer_frame = tk.Frame(
            self.sidebar,
            bg=self.sidebar_bg,
            height=160
        )
        footer_frame.pack(side="bottom", fill="x", padx=Spacing.MD, pady=Spacing.XS)
        footer_frame.pack_propagate(False)
        
        # Separador
        separator = tk.Frame(
            footer_frame,
            height=1,
            bg=theme_manager.themes[theme_manager.current_theme]["border_light"]
        )
        separator.pack(fill="x", pady=(0, Spacing.XS))

        # Botón de usuario (sobre configuración)
        self.user_frame = tk.Frame(footer_frame, bg=self.sidebar_bg)
        self.user_frame.pack(fill="x", pady=(0, Spacing.SM))

        theme = theme_manager.themes[theme_manager.current_theme]
        label_style = theme_manager.get_style("label_body").copy()
        label_style.pop('bg', None)
        label_style.pop('fg', None)  # usamos sidebar_fg más abajo

        # Obtener nombre del usuario actual
        user_display_name = self.current_user.get("full_name", self.current_user.get("username", "Admin"))

        user_btn_bg = theme.get("sidebar_bg", theme["bg_primary"])
        user_btn_fg = theme.get("sidebar_fg", theme["text_primary"])
        user_btn = tk.Button(
            self.user_frame,
            text=f"{Icons.TENANT_PROFILE} {user_display_name}",
            **label_style,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._show_user_menu,
            bg=user_btn_bg,
            fg=user_btn_fg,
            activebackground=theme.get("sidebar_hover", theme["bg_tertiary"]),
            activeforeground=user_btn_fg
        )
        user_btn.pack(fill="x")
        self.user_btn = user_btn

        # Tooltip de aviso de licencia por vencer (≤3 días)
        self._license_warning_tooltip = None
        self._license_warning_after_id = None

        def _show_license_warning_tooltip():
            if getattr(self, "_license_warning_tooltip", None) is not None:
                try:
                    if self._license_warning_tooltip.winfo_exists():
                        self._license_warning_tooltip.destroy()
                except (tk.TclError, AttributeError):
                    pass
                self._license_warning_tooltip = None
            try:
                from manager.app.services.license_service import license_service
                st = license_service.get_status()
                if st.get("mode") != "licensed":
                    return
                rem = st.get("remaining_days")
                if rem is None or rem > 3:
                    return
            except Exception:
                return
            tip = tk.Toplevel(self.root)
            self._license_warning_tooltip = tip
            tip.overrideredirect(True)
            tip.attributes("-topmost", True)
            tip.configure(bg="#fef3c7")
            txt = f"⚠️ Tu licencia vence en {rem} día(s). Renueva en Licencia."
            lbl = tk.Label(tip, text=txt, font=("Segoe UI", 9), bg="#fef3c7", fg="#92400e", padx=10, pady=6, wraplength=220)
            lbl.pack()
            try:
                tip.update_idletasks()
                bx = self.user_frame.winfo_rootx() + self.user_frame.winfo_width() + 6
                by = self.user_frame.winfo_rooty()
                tip.geometry(f"+{bx}+{by}")
            except Exception:
                pass

        def on_enter(e):
            t = theme_manager.themes[theme_manager.current_theme]
            hover_bg = t.get("sidebar_hover", t["bg_tertiary"])
            hover_fg = t.get("sidebar_fg", t["text_primary"])
            user_btn.configure(bg=hover_bg, activebackground=hover_bg, fg=hover_fg, activeforeground=hover_fg)
            self._hide_license_warning_tooltip()
            self._license_warning_after_id = self.root.after(500, _show_license_warning_tooltip)

        def on_leave(e):
            self._hide_license_warning_tooltip()
            try:
                root = user_btn.winfo_toplevel()
                root.update_idletasks()
                px = root.winfo_pointerx()
                py = root.winfo_pointery()
                w = root.winfo_containing(px, py)
            except (tk.TclError, AttributeError):
                w = None
            if w is not None:
                cur = w
                while cur:
                    if cur == user_btn or cur == self.user_frame:
                        return
                    try:
                        cur = cur.master
                    except (tk.TclError, AttributeError):
                        break
            t = theme_manager.themes[theme_manager.current_theme]
            orig_bg = t.get("sidebar_bg", t["bg_primary"])
            orig_fg = t.get("sidebar_fg", t["text_primary"])
            user_btn.configure(bg=orig_bg, activebackground=t.get("sidebar_hover", t["bg_tertiary"]), fg=orig_fg, activeforeground=orig_fg)

        user_btn.bind("<Enter>", on_enter)
        user_btn.bind("<Leave>", on_leave)
        
        # Botón de configuración (mismo estilo y hover que el resto del menú lateral)
        settings_btn = self._create_nav_button(
            footer_frame,
            {
                "text": "Configuración",
                "icon": Icons.SETTINGS,
                "command": lambda: self._navigate_to("settings"),
                "active": False
            }
        )
        # Usar colores del sidebar como el resto de ítems (no bg_primary) para hover uniforme
        theme = theme_manager.themes[theme_manager.current_theme]
        sidebar_bg = theme.get("sidebar_bg", theme["bg_secondary"])
        sidebar_fg = theme.get("sidebar_fg", theme["text_primary"])
        settings_btn.configure(bg=sidebar_bg, relief="flat", bd=0, highlightthickness=0)
        if hasattr(settings_btn, 'inner_frame') and settings_btn.inner_frame.winfo_exists():
            settings_btn.inner_frame.configure(bg=sidebar_bg, highlightthickness=0)
        if hasattr(settings_btn, 'icon_label') and settings_btn.icon_label.winfo_exists():
            settings_btn.icon_label.configure(bg=sidebar_bg, fg=sidebar_fg)
        if hasattr(settings_btn, 'text_label') and settings_btn.text_label.winfo_exists():
            settings_btn.text_label.configure(bg=sidebar_bg, fg=sidebar_fg, font=("Segoe UI", 11, "bold"))
        # Agregar al diccionario de botones para que también se actualice el estado activo
        if not hasattr(self, 'nav_buttons'):
            self.nav_buttons = {}
        self.nav_buttons["configuración"] = settings_btn
    
    def _create_content_area(self, parent):
        """Crea el área de contenido principal"""
        theme = theme_manager.themes[theme_manager.current_theme]
        self.content_bg = theme.get("content_bg", "#f1f5f9")  # slate-100: fondo neutro para contrastar con cards azules
        self.content_frame = tk.Frame(
            parent,
            **theme_manager.get_style("frame"),
            bd=0,
            highlightthickness=0
        )
        self.content_frame.configure(bg=self.content_bg)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Overlay que tapa la línea gris: en el main_frame justo sobre el límite (sidebar 280 + edge 6 = 286px)
        self.content_edge_overlay = tk.Frame(
            parent,
            width=14,
            bg=self.sidebar_bg,
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.content_edge_overlay.place(x=282, y=0, relheight=1, width=14)
        
        # Header del contenido
        self._create_content_header()
        
        # Área de vistas
        self.views_container = tk.Frame(
            self.content_frame,
            **theme_manager.get_style("frame")
        )
        self.views_container.configure(bg=self.content_bg)
        self.views_container.pack(fill="both", expand=True, padx=Spacing.XL, pady=(0, Spacing.MD))
        
        # Cargar vista inicial
        self._navigate_to("dashboard")
        
        # Overlay en main_frame: subirlo al frente para que quede encima del borde entre sidebar y contenido
        self.content_edge_overlay.lift()
    
    def _create_content_header(self):
        """Crea el header del área de contenido (barra del título desde el borde superior)"""
        theme = theme_manager.themes[theme_manager.current_theme]
        self.header_bg = theme.get("header_bg", "#e84118")
        self.content_header_frame = tk.Frame(
            self.content_frame,
            **theme_manager.get_style("frame"),
            height=120
        )
        self.content_header_frame.configure(bg=self.header_bg)
        # Espacio bajo el título reducido a la mitad (Spacing.MD) para todas las vistas
        self.content_header_frame.pack(fill="x", pady=(0, Spacing.MD))
        self.content_header_frame.pack_propagate(False)
        
        # Título dibujado con Canvas: contorno blanco de 1px en cada letra (sin recuadro)
        self._page_title_text = "Dashboard"
        self.page_title_canvas = tk.Canvas(
            self.content_header_frame,
            bg=self.header_bg,
            highlightthickness=0
        )
        self.page_title_canvas.pack(fill="both", expand=True)
        self.page_title_canvas.bind("<Configure>", lambda e: self._draw_page_title())
        self._draw_page_title()
    
    def _draw_page_title(self):
        """Dibuja el título del header con contorno sutil (color suave, 1px en 4 direcciones)"""
        c = getattr(self, "page_title_canvas", None)
        if not c or not c.winfo_exists():
            return
        c.delete("page_title")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            return
        x, y = w // 2, h // 2
        text = getattr(self, "_page_title_text", "Dashboard")
        theme = theme_manager.themes[theme_manager.current_theme]
        fg = "#ffffff"
        font = ("Segoe UI", 32, "bold")
        # Contorno sutil: 0.5px en 4 direcciones (más fino)
        #outline_color = "#e0dcd8"
        #for dx, dy in ((0, -0.5), (0, 0.5), (-0.5, 0), (0.5, 0)):
         #   c.create_text(x + dx, y + dy, text=text, font=font, fill=outline_color, anchor="center", tags="page_title")
        c.create_text(x, y, text=text, font=font, fill=fg, anchor="center", tags="page_title")
    
    def _navigate_to(self, view_name: str):
        """Navega a una vista específica (delega en AppController)."""
        self.app_controller.navigate_to(view_name)

    # --- API para AppController (orquestación de navegación) ---
    def set_current_view(self, view_name: str) -> None:
        """Establece la vista actual (estado interno)."""
        self._current_view = view_name

    def update_nav_buttons(self, active_view: str) -> None:
        """Actualiza el estado visual de los botones del menú lateral."""
        self._update_nav_buttons(active_view)

    def set_page_title(self, title: str) -> None:
        """Establece y redibuja el título de la página."""
        self._page_title_text = title
        self._draw_page_title()

    def clear_views_container(self) -> None:
        """Destruye todos los widgets del área de contenido."""
        for widget in self.views_container.winfo_children():
            widget.destroy()

    def load_view(self, view_name: str) -> None:
        """Carga e inserta la vista correspondiente en el contenedor."""
        self._load_view(view_name)

    def get_root(self):
        """Devuelve la ventana raíz (tk.Tk) para programar actualizaciones."""
        return self.root

    def force_tenants_refresh(self) -> None:
        """Fuerza un refresh completo de la vista de inquilinos (tras navegación)."""
        self._force_tenants_refresh()

    def _update_nav_buttons(self, active_view: str):
        """Actualiza el estado visual de los botones de navegación"""
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Mapeo de nombres de vista a nombres de botones en el menú
        view_to_button = {
            "dashboard": "dashboard",
            "tenants": "inquilinos",
            "payments": "pagos",
            "expenses": "gastos",
            "administration": "administración",
            "reports": "reportes",
            "settings": "configuración"
        }
        
        active_button_name = view_to_button.get(active_view, "").lower()
        
        for view_name, btn_frame in self.nav_buttons.items():
            # Verificar si este botón es el activo
            is_active = view_name.lower() == active_button_name
            
            if is_active:
                # Estilo para botón activo: fondo ligeramente más oscuro/claro y texto más vivo
                if theme_manager.current_theme == "dark":
                    # En tema oscuro, usar un fondo ligeramente más claro
                    active_bg = theme.get("bg_tertiary", "#374151")
                    active_text_color = theme.get("text_accent", "#60a5fa")  # Color más vivo
                else:
                    # En tema claro, usar un fondo ligeramente más oscuro
                    active_bg = theme.get("bg_tertiary", "#f3f4f6")
                    active_text_color = theme.get("text_accent", "#2563eb")  # Color más vivo
                
                # Aplicar estilo activo
                btn_frame.configure(bg=active_bg)
                
                # Actualizar widgets hijos si existen
                if hasattr(btn_frame, 'inner_frame') and btn_frame.inner_frame.winfo_exists():
                    btn_frame.inner_frame.configure(bg=active_bg)
                else:
                    for child in btn_frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            child.configure(bg=active_bg)
                
                # Actualizar icono y texto
                if hasattr(btn_frame, 'icon_label') and btn_frame.icon_label.winfo_exists():
                    btn_frame.icon_label.configure(bg=active_bg, fg=active_text_color)
                if hasattr(btn_frame, 'text_label') and btn_frame.text_label.winfo_exists():
                    btn_frame.text_label.configure(
                        bg=active_bg, 
                        fg=active_text_color,
                        font=("Segoe UI", 11, "bold")  # Texto en negrita para el activo
                    )
            else:
                # Estilo normal para botones inactivos: mismo color que el sidebar (no blanco)
                bg_color = theme.get("sidebar_bg", theme["bg_secondary"])
                text_color = theme.get("sidebar_fg", theme["text_primary"])
                
                # Actualizar frame principal
                btn_frame.configure(bg=bg_color)
                
                # Actualizar widgets hijos si existen
                if hasattr(btn_frame, 'inner_frame') and btn_frame.inner_frame.winfo_exists():
                    btn_frame.inner_frame.configure(bg=bg_color)
                else:
                    for child in btn_frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            child.configure(bg=bg_color)
                
                # Actualizar icono y texto
                if hasattr(btn_frame, 'icon_label') and btn_frame.icon_label.winfo_exists():
                    btn_frame.icon_label.configure(bg=bg_color, fg=text_color)
                if hasattr(btn_frame, 'text_label') and btn_frame.text_label.winfo_exists():
                    btn_frame.text_label.configure(
                        bg=bg_color, 
                        fg=text_color,
                        font=("Segoe UI", 11, "bold")  # Módulos del menú en negrita
                    )
    
    def _load_view(self, view_name: str):
        """Carga una vista específica"""
        if view_name == "dashboard":
            dashboard = DashboardView(
                self.views_container,
                presenter=self._dashboard_presenter,
                on_new_tenant=self._show_new_tenant_form,
                on_register_expense=self._show_register_expense_direct,
                on_register_payment=self._show_register_payment_direct,
                on_search=self._show_search_dialog,
                on_occupation_status=self._show_occupation_status_direct,
                on_pending_payments=self._show_pending_payments,
            )
            dashboard.pack(fill="both", expand=True)
        elif view_name == "tenants":
            # Recargar datos de inquilinos antes de crear la vista para asegurar datos actualizados
            try:
                # Recargar datos desde archivo
                tenant_service._load_data()
                # Recalcular estados basándose en pagos recientes
                tenant_service.recalculate_all_payment_statuses()
                # Recargar datos después del recálculo
                tenant_service._load_data()
            except Exception as e:
                logger.warning("Error al recargar datos de inquilinos: %s", e)
            
            self._create_tenants_view()
            # Forzar actualización después de cargar la vista de inquilinos
            self.root.after(100, self.root.update_idletasks)
            self.root.after(200, self.root.update)
        elif view_name == "payments":
            payments_view = PaymentsView(
                self.views_container, 
                on_back=lambda: self._navigate_to("dashboard"),
                on_payment_saved=self._on_payment_saved_go_to_tenants
            )
            payments_view.pack(fill="both", expand=True)
        elif view_name == "expenses":
            expenses_view = ExpensesView(self.views_container, on_back=lambda: self._navigate_to("dashboard"))
            expenses_view.pack(fill="both", expand=True)
        elif view_name == "administration":
            self._create_administration_view()
        elif view_name == "reports":
            reports_view = ReportsView(
                self.views_container,
                on_back=lambda: self._navigate_to("dashboard"),
                on_show_occupancy_vacancy_report=self._show_occupancy_vacancy_report_from_reports,
                on_show_pending_payments_report=self._show_pending_payments
            )
            reports_view.pack(fill="both", expand=True)
        elif view_name == "settings":
            settings_view = SettingsView(self.views_container, on_back=lambda: self._navigate_to("dashboard"))
            settings_view.pack(fill="both", expand=True)
    
    def _create_tenants_view(self):
        """Crea la vista de inquilinos y abre directamente la vista de lista/detalles (sin menú de 3 cards)."""
        tenants_view = TenantsView(
            self.views_container,
            on_navigate=self._navigate_to,
            on_data_change=self.refresh_dashboard,  # Callback para actualizar dashboard
            on_register_payment=self.navigate_to_payments,
            on_new_tenant=self._show_new_tenant_form,
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
        # Fondo igual al área de contenido para que el frame se vea transparente
        bg_content = getattr(self, "content_bg", theme_manager.themes[theme_manager.current_theme].get("content_bg", "#f1f5f9"))
        admin_frame = tk.Frame(self.views_container, bg=bg_content)
        admin_frame.pack(fill="both", expand=True)
        
        # Header con botones de navegación
        header_frame = tk.Frame(admin_frame, bg=bg_content)
        header_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.XL)
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header_frame, bg=bg_content)
        buttons_frame.pack(side="right")
        
        # Agregar solo botón Dashboard (sin Volver porque es redundante)
        self._create_navigation_buttons(buttons_frame, lambda: self._navigate_to("dashboard"), show_back_button=False)

        # Título encima de los cards (como en el módulo de Gastos: "¿Qué deseas hacer?")
        theme = theme_manager.themes[theme_manager.current_theme]
        question_label = tk.Label(
            admin_frame,
            text="¿Qué gestión desea hacer?",
            font=("Segoe UI", 14),
            fg=theme["text_primary"],
            bg=bg_content
        )
        question_label.pack(pady=(0, Spacing.XL))

        # Verificar si ya existe un edificio para la versión profesional
        from manager.app.services.building_service import building_service
        has_existing_building = building_service.has_buildings()

        actions_grid = [
            {
                "icon": "🏗️",
                "title": "Crear Nuevo Edificio",
                "description": "Configura un nuevo edificio con sus apartamentos y características.",
                "color": "#6d28d9",  # morado más intenso para mayor contraste
                "action": self._show_building_setup_view,
                "enabled": not has_existing_building,  # Deshabilitar si ya existe un edificio
                "disabled_message": "Ya existe un edificio configurado"
            },
            {
                "icon": "🏢",
                "title": "Gestionar Edificio" if has_existing_building else "Gestionar Edificios",
                "description": "Edita los detalles del edificio, dirección y configuración general.",
                "color": "#6d28d9",  # morado más intenso para mayor contraste
                "action": self._show_building_management_view,
                "enabled": True
            },
            {
                "icon": "🛋️",
                "title": "Gestión de Apartamentos",
                "description": "Administra apartamentos, estados de ocupación y detalles.",
                "color": "#6d28d9",  # morado más intenso para mayor contraste
                "action": self._show_apartment_management_view,
                "enabled": True
            },
            {
                "icon": "💾",
                "title": "Backup de Datos",
                "description": "Crea y restaura copias de seguridad completas del sistema.",
                "color": "#6d28d9",  # morado más intenso para mayor contraste
                "action": self._show_backup_view,
                "enabled": True
            },
            {
                "icon": "⚙️",
                "title": "Gestión de Usuarios",
                "description": "Administra usuarios del sistema, roles y permisos de acceso.",
                "color": "#6d28d9",  # morado más intenso para mayor contraste
                "action": self._show_user_management_view,
                "enabled": True
            }
        ]
        
        # Crear filas de 3 tarjetas cada una con tamaño uniforme usando grid
        num_columns = 3
        num_rows = (len(actions_grid) + num_columns - 1) // num_columns  # Calcular número de filas
        
        # Contenedor para el grid con distribución uniforme (fondo transparente)
        grid_container = tk.Frame(admin_frame, bg=bg_content)
        grid_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)
        
        # Tamaño similar a Reportes (175x130) para que quepan las 2 filas en vista
        CARD_HEIGHT = 150
        row_minsize = CARD_HEIGHT + 2 * Spacing.MD
        # Configurar el grid para distribución uniforme
        for col in range(num_columns):
            grid_container.grid_columnconfigure(col, weight=1, uniform="col")
        for row in range(num_rows):
            grid_container.grid_rowconfigure(row, weight=1, uniform="row", minsize=row_minsize)
        
        row_num = 0
        for i in range(0, len(actions_grid), num_columns):
            row_items = actions_grid[i:i+num_columns]
            for col, item in enumerate(row_items):
                card = self._create_admin_action_card(
                    grid_container, item["icon"], item["title"], item.get("description", ""), item["color"], 
                    item["action"], item.get("enabled", True), item.get("disabled_message", "")
                )
                card.grid(row=row_num, column=col, sticky="nsew", padx=Spacing.MD, pady=Spacing.MD)
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
    
    def _show_new_tenant_form(self):
        """Muestra directamente el formulario de nuevo inquilino"""
        # Actualizar estado de botones de navegación para inquilinos
        self._update_nav_buttons("tenants")
        
        # Actualizar título
        self._page_title_text = "Nuevo Inquilino"
        self._draw_page_title()
        
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
            on_register_payment=self.navigate_to_payments,
            on_new_tenant=self._show_new_tenant_form,
        )
        tenants_view._show_tenants_list()  # Ir directo a la vista de detalles
        tenants_view.pack(fill="both", expand=True)
    
    def _show_pending_payments(self):
        """Muestra el reporte de pagos pendientes (contenido generado por ReportPresenter)."""
        try:
            report_content = self._report_presenter.get_pending_payments_report_text()
            if not report_content:
                messagebox.showinfo(
                    "Sin datos", "No hay inquilinos con pagos pendientes."
                )
                return
            show_pending_payments_report(
                self.root, report_content, self._show_export_success_dialog
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al generar reporte de pendientes: {str(e)}"
            )

    def _show_export_success_dialog(self, filepath: Path):
        """Diálogo de confirmación tras exportar: Copiar, Abrir carpeta, Abrir archivo, Aceptar (reglas establecidas)."""
        colors = get_module_colors("reportes")
        win = tk.Toplevel(self.root)
        win.title("Exportación exitosa")
        win.geometry("520x220")
        win.transient(self.root)
        win.resizable(True, False)
        win.grab_set()
        content_f = tk.Frame(win, padx=Spacing.LG, pady=Spacing.LG)
        content_f.pack(fill="both", expand=True)
        top = tk.Frame(content_f)
        top.pack(fill="x")
        tk.Label(top, text="ℹ", font=("Segoe UI", 28), fg=colors.get("primary", "#ea580c")).pack(side="left", padx=(0, Spacing.MD))
        msg = tk.Frame(top)
        msg.pack(side="left", fill="x", expand=True)
        tk.Label(msg, text="Exportación exitosa. Archivo guardado en:", font=("Segoe UI", 11)).pack(anchor="w")
        path_var = tk.StringVar(value=str(filepath))
        path_entry = tk.Entry(msg, textvariable=path_var, font=("Segoe UI", 10))
        path_entry.pack(fill="x", pady=(Spacing.SM, 0))
        path_entry.bind("<Key>", lambda e: "break")
        btns = tk.Frame(content_f)
        btns.pack(fill="x", pady=(Spacing.LG, 0))
        def copy_path():
            win.clipboard_clear()
            win.clipboard_append(str(filepath))
        def open_folder():
            folder = str(filepath.resolve().parent)
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.run(["xdg-open", folder], check=False)
        def open_file():
            path = str(filepath.resolve())
            if os.name == "nt":
                os.startfile(path)
            else:
                subprocess.run(["xdg-open", path], check=False)
        tk.Button(btns, text="📋 Copiar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=copy_path).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📁 Abrir carpeta", font=("Segoe UI", 10), bg="#6b7280", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_folder).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📄 Abrir archivo", font=("Segoe UI", 10), bg="#059669", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_file).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="Aceptar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=win.destroy).pack(side="right")
    
    def _show_occupation_status_direct(self):
        """Navega al módulo de administración de apartamentos y muestra la vista de estado de ocupación"""
        # Actualizar título y botones de navegación
        self._update_nav_buttons("administration")
        self._page_title_text = "Gestión de Apartamentos"
        self._draw_page_title()
        
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Crear la vista de administración de apartamentos
        apartment_view = ApartmentManagementView(self.views_container, on_navigate=self._navigate_to)
        apartment_view.pack(fill="both", expand=True)
        
        # Mostrar directamente la vista de estado de ocupación dentro del módulo
        apartment_view._show_occupation_status()

    def _show_occupancy_vacancy_report_from_reports(self):
        """Muestra la misma vista del reporte de ocupación y vacancia (desde el card Reporte Financiero Consolidado)."""
        self._update_nav_buttons("reports")
        self._page_title_text = "Reportes y Análisis"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        report_view = OccupancyVacancyReportView(
            self.views_container,
            on_back=lambda: self._navigate_to("reports"),
            on_navigate=self._navigate_to,
            module_context="reportes"
        )
        report_view.pack(fill="both", expand=True)
        self.current_view = report_view

    def _show_backup_view(self):
        """Muestra la vista de gestión de backups"""
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Crear la vista de backup
        backup_view = BackupView(
            self.views_container,
            on_back=lambda: self._navigate_to("administration"),
            on_navigate=self._navigate_to
        )
        backup_view.pack(fill="both", expand=True)
        
        self.current_view = backup_view
    
    def _show_user_management_view(self):
        """Muestra la vista de gestión de usuarios"""
        # Limpiar contenido actual
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Crear la vista de gestión de usuarios
        user_view = UserManagementView(
            self.views_container,
            on_back=lambda: self._navigate_to("administration"),
            on_navigate=self._navigate_to
        )
        user_view.pack(fill="both", expand=True)
    
    def _show_apartment_management_view(self):
        """Muestra la vista de gestión de apartamentos"""
        self._page_title_text = "Gestión de Apartamentos"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        apartment_view = ApartmentManagementView(self.views_container, on_navigate=self._navigate_to)
        apartment_view.pack(fill="both", expand=True)

    def _show_placeholder_dialog(self, title: str, message: str):
        """Muestra un diálogo placeholder para funcionalidades futuras"""
        messagebox.showinfo(title, f"{message}\n\nEsta funcionalidad será implementada próximamente.")

    def _create_admin_action_card(self, parent, icon: str, title: str, description: str, color: str, action: Callable, enabled: bool = True, disabled_message: str = ""):
        """Crea una card de acción administrativa con el mismo formato que los cards de inquilinos/pagos/gastos"""
        # Color morado más intenso para el fondo base de las tarjetas (similar al hover anterior)
        light_purple_bg = "#f3e8ff"  # purple-100 - morado claro más intenso para mejor contraste con iconos morados
        
        # Ajustar estilo según si está habilitada o no
        if enabled:
            bg_color = light_purple_bg
            cursor = "hand2"
        else:
            bg_color = "#f5f5f5"  # Gris claro para deshabilitado
            cursor = "arrow"
            color = "#999999"  # Gris para icono y texto deshabilitado
        
        # Tamaño reducido para que quepan las 6 cards en vista (similar a Reportes)
        card = tk.Frame(parent, bg=bg_color, bd=2, relief="raised", width=200, height=150)
        card.pack_propagate(False)
        card.configure(cursor=cursor)
        
        # Contenedor principal con padding uniforme para centrar verticalmente
        content_frame = tk.Frame(card, bg=bg_color)
        content_frame.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Frame espaciador superior para centrar el contenido
        top_spacer = tk.Frame(content_frame, bg=bg_color, height=1)
        top_spacer.pack(fill="x", expand=True)
        
        # Contenedor del contenido (icono, título) - centrado verticalmente
        content_container = tk.Frame(content_frame, bg=bg_color)
        content_container.pack()
        
        # Ícono con tamaño reducido (similar a reportes)
        icon_label = tk.Label(content_container, text=icon, font=("Segoe UI Symbol", 22), 
                             fg=color, bg=bg_color)
        icon_label.pack(pady=(0, Spacing.SM))
        
        # Título con color morado unificado
        title_color = "#000000" if enabled else "#999999"  # Título en negro para mayor contraste
        title_label = tk.Label(content_container, text=title, font=("Segoe UI", 11, "bold"), 
                              fg=title_color, bg=bg_color, wraplength=180, justify="center")
        title_label.pack()
        
        # Textos descriptivos eliminados según solicitud del usuario
        
        # Frame espaciador inferior para centrar el contenido
        bottom_spacer = tk.Frame(content_frame, bg=bg_color, height=1)
        bottom_spacer.pack(fill="x", expand=True)
        
        # Función para manejar clics - se ejecuta desde cualquier parte del card
        def on_card_click(e):
            if enabled:
                e.widget.focus_set()
                action()
                return "break"
        
        # Hover effect solo si está habilitada
        if enabled:
            hover_bg_color = "#e9d5ff"  # purple-200 - morado más intenso para hover
            def on_enter(e):
                hover_bg = hover_bg_color
                card.configure(bg=hover_bg)
                content_frame.configure(bg=hover_bg)
                top_spacer.configure(bg=hover_bg)
                content_container.configure(bg=hover_bg)
                bottom_spacer.configure(bg=hover_bg)
                icon_label.configure(bg=hover_bg)
                title_label.configure(bg=hover_bg, fg=title_color)
            
            def on_leave(e):
                card.configure(bg=bg_color)
                content_frame.configure(bg=bg_color)
                top_spacer.configure(bg=bg_color)
                content_container.configure(bg=bg_color)
                bottom_spacer.configure(bg=bg_color)
                icon_label.configure(bg=bg_color)
                title_label.configure(bg=bg_color, fg=title_color)
            
            # Hacer TODO el card clickeable - bind a todos los elementos
            all_widgets = [card, content_frame, top_spacer, content_container, bottom_spacer, icon_label, title_label]
            
            for widget in all_widgets:
                widget.bind("<Button-1>", on_card_click)
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.configure(cursor="hand2")
        else:
            # Si está deshabilitada, mostrar tooltip al hacer hover
            def show_disabled_tooltip(e):
                if disabled_message:
                    tooltip = tk.Toplevel(card)
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
                    card.bind("<Leave>", hide_tooltip)
            
            card.bind("<Enter>", show_disabled_tooltip)
        
        return card
    
    def _create_navigation_buttons(self, parent, on_back_command, show_back_button=True, module_name="administración"):
        """Crea los botones Volver y Dashboard con estilo moderno y colores del módulo"""
        # Colores según el módulo (por defecto administración/morado)
        colors = get_module_colors(module_name)
        primary = colors["primary"]
        hover = colors["hover"]
        light = colors["light"]
        text_color = colors["text"]
        
        # Botón "Volver" (solo si show_back_button es True)
        if show_back_button:
            btn_back = create_rounded_button(
                parent,
                text=f"{Icons.ARROW_LEFT} Volver",
                bg_color="white",
                fg_color=primary,
                hover_bg=light,
                hover_fg=text_color,
                command=on_back_command,
                padx=16,
                pady=8,
                radius=4,
                border_color="#000000"
            )
            btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard)
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=primary,
            fg_color="white",
            hover_bg=hover,
            hover_fg="white",
            command=lambda: self._navigate_to("dashboard"),
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")
    
    def refresh_dashboard(self):
        """Refresca las estadísticas del dashboard"""
        current_view = getattr(self, "_current_view", None)
        if current_view == "dashboard":
            for widget in self.views_container.winfo_children():
                widget.destroy()
            dashboard = DashboardView(
                self.views_container,
                presenter=self._dashboard_presenter,
                on_new_tenant=self._show_new_tenant_form,
                on_register_expense=self._show_register_expense_direct,
                on_register_payment=self._show_register_payment_direct,
                on_search=self._show_search_dialog,
                on_occupation_status=self._show_occupation_status_direct,
                on_pending_payments=self._show_pending_payments,
            )
            dashboard.pack(fill="both", expand=True)
    
    def _on_payment_saved_go_to_tenants(self):
        """Tras registrar un pago: refresca datos y navega al listado de inquilinos."""
        self.refresh_tenants_view()
        self._navigate_to("tenants")

    def refresh_tenants_view(self):
        """Refresca la vista de inquilinos para mostrar estados actualizados en tiempo real"""
        current_view = getattr(self, '_current_view', None)
        logger.debug("Refrescando vista de inquilinos desde vista: %s", current_view)
        
        try:
            # Primero intentar refrescar si la vista de inquilinos ya está activa
            if current_view == "tenants":
                # Buscar la instancia de TenantsView en los widgets hijos
                for widget in self.views_container.winfo_children():
                    if isinstance(widget, TenantsView):
                        # Si está en la lista, refrescar solo la lista sin destruir la vista
                        if widget.current_view == "list":
                            widget.refresh_list()
                            logger.debug("Lista de inquilinos refrescada en tiempo real (sin recrear vista)")
                            # Forzar actualización de la UI
                            self.root.update_idletasks()
                            self.root.update()
                            return
                        # Si está en otra subvista (dashboard, details), refrescar cuando vuelva a lista
            
            # Si no estamos en la vista de inquilinos o no está en lista,
            # los datos se recargarán al navegar a inquilinos vía _create_tenants_view()
            logger.debug("Callback de refresh ejecutado - Los datos se actualizarán al navegar a inquilinos")
        except Exception as e:
            logger.warning("Error al refrescar vista de inquilinos: %s", e)
    
    def _force_tenants_refresh(self):
        """Fuerza un refresh completo de la vista de inquilinos"""
        logger.debug("Forzando refresh completo de vista de inquilinos")
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
        except Exception as e:
            logger.warning("Error al forzar refresh: %s", e)
    
    def _show_register_payment_direct(self):
        """Navega a la vista de pagos y abre directamente el registro de pago"""
        # Limpiar contenido actual
        self._update_nav_buttons("payments")
        self._page_title_text = "Registrar pagos"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        payments_view = PaymentsView(
            self.views_container, 
            on_back=lambda: self._navigate_to("dashboard"),
            on_payment_saved=self._on_payment_saved_go_to_tenants
        )
        payments_view.pack(fill="both", expand=True)
        payments_view._show_register_payment()
    
    def navigate_to_payments(self, tenant=None):
        """Navega a la vista de pagos y abre el formulario con el inquilino preseleccionado si se proporciona."""
        self._update_nav_buttons("payments")
        self._page_title_text = "Registrar pagos"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        payments_view = PaymentsView(
            self.views_container, 
            on_back=lambda: self._navigate_to("dashboard"), 
            preselected_tenant=tenant,
            on_payment_saved=self._on_payment_saved_go_to_tenants
        )
        payments_view.pack(fill="both", expand=True)
        payments_view._show_register_payment(preselected_tenant=tenant)
    
    def _show_register_expense_direct(self):
        """Navega a la vista de gastos y abre directamente el registro de gasto"""
        self._update_nav_buttons("expenses")
        self._page_title_text = "Gestión de Gastos"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        expenses_view = ExpensesView(
            self.views_container, 
            on_back=lambda: self._navigate_to("dashboard")
        )
        expenses_view.pack(fill="both", expand=True)
        expenses_view._show_register_expense()
    
    def _show_building_setup_view(self):
        """Muestra el asistente de configuración del edificio."""
        self._page_title_text = "Configuración del Edificio"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        setup_view = BuildingSetupView(self.views_container, on_back=lambda: self._navigate_to("administration"))
        setup_view.pack(fill="both", expand=True)

    def _show_building_management_view(self):
        """Muestra la vista para gestionar edificios existentes."""
        self._page_title_text = "Gestión de Edificios"
        self._draw_page_title()
        for widget in self.views_container.winfo_children():
            widget.destroy()
        
        # Pasar referencia a MainWindow para que pueda navegar al dashboard
        management_view = BuildingManagementView(
            self.views_container, 
            on_back=lambda: self._navigate_to("administration"),
            main_window_ref=self  # Pasar referencia para navegación al dashboard
        )
        management_view.pack(fill="both", expand=True)

    def _hide_license_warning_tooltip(self):
        """Oculta el tooltip de aviso de licencia por vencer (si existe)."""
        aid = getattr(self, "_license_warning_after_id", None)
        if aid is not None:
            try:
                self.root.after_cancel(aid)
            except (tk.TclError, AttributeError):
                pass
            self._license_warning_after_id = None
        tip = getattr(self, "_license_warning_tooltip", None)
        if tip is not None:
            try:
                if tip.winfo_exists():
                    tip.destroy()
            except (tk.TclError, AttributeError):
                pass
            self._license_warning_tooltip = None

    def _show_user_menu(self):
        """Muestra el menú desplegable del usuario"""
        self._hide_license_warning_tooltip()
        # Toggle: si ya está abierto, cerrarlo
        try:
            if hasattr(self, "user_menu_window") and self.user_menu_window.winfo_exists():
                self.user_menu_window.destroy()
                self.user_menu_window = None
                return
        except (tk.TclError, AttributeError):
            self.user_menu_window = None

        # Bind global para cerrar con Escape y click fuera (una sola vez)
        if not hasattr(self, "_user_menu_bindings_ready"):
            self.root.bind_all("<Escape>", self._on_user_menu_escape, add="+")
            self.root.bind_all("<Button-1>", self._on_root_click_close_user_menu, add="+")
            self._user_menu_bindings_ready = True

        # Crear ventana de menú
        menu_window = tk.Toplevel(self.root)
        self.user_menu_window = menu_window
        menu_window.withdraw()  # Ocultar temporalmente
        menu_window.overrideredirect(True)
        menu_window.attributes("-topmost", False)
        
        # Obtener posición del botón
        self.user_frame.update_idletasks()
        x = self.user_frame.winfo_rootx()
        menu_width = 200
        
        # Frame del menú
        theme = theme_manager.themes[theme_manager.current_theme]
        menu_frame = tk.Frame(
            menu_window,
            bg=theme["bg_secondary"],
            relief="solid",
            bd=1
        )
        menu_frame.pack(fill="both", expand=True)
        
        # Información del usuario
        user_info_frame = tk.Frame(menu_frame, bg=theme["bg_secondary"])
        user_info_frame.pack(fill="x", padx=8, pady=6)
        
        # Nombre completo
        user_display_name = self.current_user.get("full_name", self.current_user.get("username", "Admin"))
        user_name_label = tk.Label(
            user_info_frame,
            text=user_display_name,
            font=("Segoe UI", 9, "bold"),
            bg=theme["bg_secondary"],
            fg=theme["text_primary"]
        )
        user_name_label.pack(anchor="w")
        
        # Rol del usuario
        user_role = self.current_user.get("role", "admin")
        role_display = self.user_service.ROLES.get(user_role, user_role.capitalize())
        role_label = tk.Label(
            user_info_frame,
            text=role_display,
            font=("Segoe UI", 8),
            bg=theme["bg_secondary"],
            fg=theme["text_secondary"]
        )
        role_label.pack(anchor="w", pady=(1, 0))

        # Aviso si la licencia vence en 3 días o menos
        try:
            from manager.app.services.license_service import license_service
            st = license_service.get_status()
            if st.get("mode") == "licensed":
                rem = st.get("remaining_days")
                if rem is not None and rem <= 3:
                    warn_frame = tk.Frame(menu_frame, bg="#fef3c7")
                    warn_frame.pack(fill="x", padx=6, pady=(4, 4))
                    msg = f"⚠️ Tu licencia vence en {rem} día(s). Renueva en Licencia."
                    tk.Label(
                        warn_frame,
                        text=msg,
                        font=("Segoe UI", 8),
                        bg="#fef3c7",
                        fg="#92400e",
                        wraplength=menu_width - 20,
                        justify="left",
                    ).pack(anchor="w", padx=6, pady=4)
        except Exception:
            pass
        
        # Separador
        separator = tk.Frame(menu_frame, bg=theme["bg_tertiary"], height=1)
        separator.pack(fill="x", padx=5, pady=3)
        
        # Opciones del menú
        options_frame = tk.Frame(menu_frame, bg=theme["bg_secondary"])
        options_frame.pack(fill="x", padx=5, pady=3)
        
        # Ver información
        def on_profile_click():
            try:
                if menu_window.winfo_exists():
                    menu_window.destroy()
            except (tk.TclError, AttributeError):
                pass
            self.root.after(10, self._show_user_profile)
        
        info_btn = tk.Button(
            options_frame,
            text="👤 Ver Perfil",
            font=("Segoe UI", 8),
            bg=theme["bg_secondary"],
            fg=theme["text_primary"],
            relief="flat",
            cursor="hand2",
            anchor="w",
            command=on_profile_click
        )
        info_btn.pack(fill="x", pady=1)
        info_btn.bind("<Enter>", lambda e: info_btn.configure(bg=theme["bg_tertiary"]))
        info_btn.bind("<Leave>", lambda e: info_btn.configure(bg=theme["bg_secondary"]))

        # Separador
        separator2 = tk.Frame(menu_frame, bg=theme["bg_tertiary"], height=1)
        separator2.pack(fill="x", padx=5, pady=3)

        # Cambiar usuario
        def on_switch_user_click():
            try:
                if menu_window.winfo_exists():
                    menu_window.destroy()
            except (tk.TclError, AttributeError):
                pass
            self.root.after(10, self._switch_user)

        switch_user_btn = tk.Button(
            options_frame,
            text="🔁 Cambiar Usuario",
            font=("Segoe UI", 8),
            bg=theme["bg_secondary"],
            fg=theme["text_primary"],
            relief="flat",
            cursor="hand2",
            anchor="w",
            command=on_switch_user_click
        )
        switch_user_btn.pack(fill="x", pady=1)
        switch_user_btn.bind("<Enter>", lambda e: switch_user_btn.configure(bg=theme["bg_tertiary"]))
        switch_user_btn.bind("<Leave>", lambda e: switch_user_btn.configure(bg=theme["bg_secondary"]))

        # Licencia (acceso rápido)
        license_tooltip = {"win": None}

        def _license_status_text():
            try:
                from manager.app.services.license_service import license_service
                st = license_service.get_status()
                mode = st.get("mode")
                if mode == "licensed":
                    exp = st.get("license_expires_at")
                    exp_txt = exp.strftime("%d/%m/%Y") if exp else "N/A"
                    return f"Licencia activa (vence {exp_txt})"
                if mode == "demo":
                    return f"Demo activa ({st.get('remaining_days')} días)"
                return "Vencida: requiere activación"
            except Exception:
                return "Estado no disponible"

        def _show_license_tooltip(widget):
            try:
                if license_tooltip["win"] is not None and license_tooltip["win"].winfo_exists():
                    license_tooltip["win"].destroy()
            except Exception:
                pass

            tip = tk.Toplevel(menu_window)
            license_tooltip["win"] = tip
            tip.overrideredirect(True)
            tip.attributes("-topmost", True)
            tip.configure(bg=theme["bg_tertiary"])

            lbl = tk.Label(
                tip,
                text=_license_status_text(),
                font=("Segoe UI", 8),
                bg=theme["bg_tertiary"],
                fg=theme["text_primary"],
                padx=8,
                pady=4,
            )
            lbl.pack()

            try:
                tip.update_idletasks()
                x = widget.winfo_rootx() + widget.winfo_width() + 8
                y = widget.winfo_rooty() + 2
                tip.geometry(f"+{x}+{y}")
            except Exception:
                pass

        def _hide_license_tooltip():
            try:
                if license_tooltip["win"] is not None and license_tooltip["win"].winfo_exists():
                    license_tooltip["win"].destroy()
            except Exception:
                pass
            license_tooltip["win"] = None

        def on_license_click():
            try:
                if menu_window.winfo_exists():
                    menu_window.destroy()
            except (tk.TclError, AttributeError):
                pass
            self.root.after(10, self._show_license_details_dialog)

        license_btn = tk.Button(
            options_frame,
            text="🔑 Licencia   ℹ",
            font=("Segoe UI", 8),
            bg=theme["bg_secondary"],
            fg=theme["text_primary"],
            relief="flat",
            cursor="hand2",
            anchor="w",
            command=on_license_click,
        )
        license_btn.pack(fill="x", pady=1)
        license_btn.bind("<Enter>", lambda e: (license_btn.configure(bg=theme["bg_tertiary"]), _show_license_tooltip(license_btn)))
        license_btn.bind("<Leave>", lambda e: (license_btn.configure(bg=theme["bg_secondary"]), _hide_license_tooltip()))
        
        # Cerrar sesión
        def on_logout_click():
            try:
                if menu_window.winfo_exists():
                    menu_window.destroy()
            except (tk.TclError, AttributeError):
                pass
            self.root.after(10, self._logout)
        
        logout_btn = tk.Button(
            options_frame,
            text="🚪 Cerrar Sesión",
            font=("Segoe UI", 8),
            bg=theme["bg_secondary"],
            fg="#ff4444",
            relief="flat",
            cursor="hand2",
            anchor="w",
            command=on_logout_click
        )
        logout_btn.pack(fill="x", pady=1)
        logout_btn.bind("<Enter>", lambda e: logout_btn.configure(bg=theme["bg_tertiary"]))
        logout_btn.bind("<Leave>", lambda e: logout_btn.configure(bg=theme["bg_secondary"]))
        
        # Ajustar tamaño al contenido y ubicar arriba si hay espacio
        menu_window.update_idletasks()
        menu_height = menu_frame.winfo_reqheight()
        menu_width = max(menu_width, menu_frame.winfo_reqwidth())
        y = self.user_frame.winfo_rooty() - menu_height
        if y < 0:
            y = self.user_frame.winfo_rooty() + self.user_frame.winfo_height()
        menu_window.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
        
        # Mostrar menú
        menu_window.deiconify()
        menu_window.bind("<Escape>", self._on_user_menu_escape)
        
        # Función para cerrar el menú de forma segura
        def close_menu():
            try:
                _hide_license_tooltip()
                if menu_window.winfo_exists():
                    menu_window.destroy()
            except (tk.TclError, AttributeError):
                pass
            self.user_menu_window = None
        
        # Enfocar el menú después de un breve delay
        self.root.after(100, lambda: menu_window.focus_set() if menu_window.winfo_exists() else None)

    def _on_user_menu_escape(self, event=None):
        """Cierra el menú de usuario con Escape"""
        try:
            if hasattr(self, "user_menu_window") and self.user_menu_window.winfo_exists():
                self.user_menu_window.destroy()
                self.user_menu_window = None
                return "break"
        except (tk.TclError, AttributeError):
            self.user_menu_window = None
        return None

    def _on_root_click_close_user_menu(self, event):
        """Cierra el menú si el clic es fuera del menú y del botón usuario"""
        try:
            if not (hasattr(self, "user_menu_window") and self.user_menu_window.winfo_exists()):
                return None
            widget = event.widget
            # No cerrar si se hace clic en el botón de usuario o su contenedor
            if hasattr(self, "user_btn") and (widget == self.user_btn or widget == self.user_frame):
                return None
            # No cerrar si el clic es dentro del menú
            cur = widget
            while cur:
                if cur == self.user_menu_window:
                    return None
                try:
                    cur = cur.master
                except (tk.TclError, AttributeError):
                    break
            # Cerrar si el clic fue fuera
            self.user_menu_window.destroy()
            self.user_menu_window = None
        except (tk.TclError, AttributeError):
            self.user_menu_window = None
        return None
    
    def _show_user_profile(self):
        """Muestra el perfil del usuario actual (mantiene al usuario logueado y solo actualiza datos desde el servicio)."""
        self.user_service._load_data()
        # Refrescar datos del usuario actual desde el servicio, sin cambiar de usuario
        current_username = self.current_user.get("username")
        if current_username:
            updated = self.user_service.get_user_by_username(current_username)
            if updated:
                self.current_user = {k: v for k, v in updated.items() if k != "password_hash"}

        theme = theme_manager.themes[theme_manager.current_theme]
        bg_pri = theme["bg_primary"]
        bg_sec = theme["bg_secondary"]
        fg_pri = theme["text_primary"]
        fg_sec = theme["text_secondary"]

        profile_window = tk.Toplevel(self.root)
        profile_window.title("Perfil de Usuario")
        profile_window.resizable(True, True)
        profile_window.transient(self.root)
        profile_window.grab_set()
        profile_window.configure(bg=bg_pri)

        main_frame = tk.Frame(profile_window, bg=bg_pri)
        main_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

        canvas = tk.Canvas(main_frame, bg=bg_pri, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_pri)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Título compacto
        tk.Label(scrollable_frame, text="👤 Perfil de Usuario", font=("Segoe UI", 14, "bold"), bg=bg_pri, fg=fg_pri).pack(anchor="w", pady=(0, Spacing.SM))

        # Bloque datos del usuario (compacto)
        info_frame = tk.Frame(scrollable_frame, bg=bg_sec, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, Spacing.SM))
        user_data = [
            ("Nombre de Usuario:", self.current_user.get("username", "N/A")),
            ("Nombre Completo:", self.current_user.get("full_name", "N/A")),
            ("Email:", self.current_user.get("email", "N/A")),
            ("Rol:", self.user_service.ROLES.get(self.current_user.get("role", "admin"), "N/A")),
            ("Estado:", "Activo" if self.current_user.get("is_active", True) else "Inactivo"),
            ("Fecha de Creación:", self._format_datetime(self.current_user.get("created_at"))),
            ("Último Login:", self._format_datetime(self.current_user.get("last_login"))),
            ("Cambio de Contraseña:", self._format_datetime(self.current_user.get("password_changed_at"))),
        ]
        for label, value in user_data:
            row_frame = tk.Frame(info_frame, bg=bg_sec)
            row_frame.pack(fill="x", padx=Spacing.MD, pady=2)
            tk.Label(row_frame, text=label, font=("Segoe UI", 9, "bold"), bg=bg_sec, fg=fg_pri, width=20, anchor="w").pack(side="left")
            tk.Label(row_frame, text=str(value), font=("Segoe UI", 9), bg=bg_sec, fg=fg_sec).pack(side="left", padx=(Spacing.SM, 0))

        # Botón Cerrar centrado
        btn_container = tk.Frame(scrollable_frame, bg=bg_pri)
        btn_container.pack(fill="x", pady=(Spacing.SM, 0))
        close_btn = tk.Button(btn_container, text="Cerrar", font=("Segoe UI", 9), bg=theme.get("btn_secondary_bg", "#e5e7eb"), fg=theme.get("btn_secondary_fg", fg_pri), relief="flat", bd=0, highlightthickness=0, padx=14, pady=6, cursor="hand2", command=profile_window.destroy)
        close_btn.pack(anchor="center")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Tamaño inicial compacto (solo datos de usuario + botón)
        profile_window.update_idletasks()
        w, h = 480, 320
        x = (profile_window.winfo_screenwidth() // 2) - (w // 2)
        y = (profile_window.winfo_screenheight() // 2) - (h // 2)
        profile_window.geometry(f"{w}x{h}+{x}+{y}")
    
    def _format_datetime(self, iso_string):
        """Formatea una fecha ISO a formato legible"""
        if not iso_string:
            return "Nunca"
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return iso_string
    
    def _show_user_activity(self):
        """Muestra el historial de actividad del usuario actual"""
        
        # Recargar datos de actividad
        self.user_service._load_activity()
        
        # Obtener actividad del usuario actual
        username = self.current_user.get("username", "admin")
        user_activity = self.user_service.get_activity_log(username, limit=200)
        
        # Crear ventana de actividad
        activity_window = tk.Toplevel(self.root)
        activity_window.title("Mi Actividad")
        activity_window.geometry("800x600")
        activity_window.transient(self.root)
        activity_window.grab_set()
        
        # Centrar ventana
        activity_window.update_idletasks()
        x = (activity_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (activity_window.winfo_screenheight() // 2) - (600 // 2)
        activity_window.geometry(f"800x600+{x}+{y}")
        
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Frame principal
        main_frame = tk.Frame(activity_window, bg=theme["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=theme["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="📋 Mi Actividad",
            font=("Segoe UI", 18, "bold"),
            bg=theme["bg_primary"],
            fg=theme["text_primary"]
        )
        title_label.pack(side="left")
        
        # Estadísticas rápidas
        stats_frame = tk.Frame(header_frame, bg=theme["bg_primary"])
        stats_frame.pack(side="right")
        
        total_actions = len(user_activity)
        today_actions = len([a for a in user_activity if self._is_today(a.get("timestamp", ""))])
        
        tk.Label(
            stats_frame,
            text=f"Total: {total_actions} | Hoy: {today_actions}",
            font=("Segoe UI", 10),
            bg=theme["bg_primary"],
            fg=theme["text_secondary"]
        ).pack(side="right", padx=(10, 0))
        
        # Frame con scroll para la lista de actividad
        scroll_frame = tk.Frame(main_frame, bg=theme["bg_primary"])
        scroll_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Canvas para scroll
        canvas = tk.Canvas(scroll_frame, bg=theme["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme["bg_primary"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar actividades
        if not user_activity:
            no_activity_label = tk.Label(
                scrollable_frame,
                text="No hay actividad registrada",
                font=("Segoe UI", 12),
                bg=theme["bg_primary"],
                fg=theme["text_secondary"]
            )
            no_activity_label.pack(pady=50)
        else:
            # Agrupar actividades por fecha
            activities_by_date = {}
            for activity in user_activity:
                timestamp = activity.get("timestamp", "")
                date_key = self._get_date_key(timestamp)
                if date_key not in activities_by_date:
                    activities_by_date[date_key] = []
                activities_by_date[date_key].append(activity)
            
            # Mostrar actividades agrupadas por fecha
            for date_key in sorted(activities_by_date.keys(), reverse=True):
                # Encabezado de fecha
                date_header = tk.Frame(scrollable_frame, bg=theme["bg_secondary"], relief="solid", bd=1)
                date_header.pack(fill="x", pady=(10, 5))
                
                tk.Label(
                    date_header,
                    text=date_key,
                    font=("Segoe UI", 11, "bold"),
                    bg=theme["bg_secondary"],
                    fg=theme["text_primary"],
                    padx=15,
                    pady=8
                ).pack(side="left")
                
                # Lista de actividades del día
                for activity in activities_by_date[date_key]:
                    activity_frame = tk.Frame(scrollable_frame, bg=theme["bg_secondary"], relief="solid", bd=1)
                    activity_frame.pack(fill="x", pady=2, padx=(0, 0))
                    
                    # Frame interno con padding
                    inner_frame = tk.Frame(activity_frame, bg=theme["bg_secondary"])
                    inner_frame.pack(fill="x", padx=15, pady=10)
                    
                    # Hora y tipo de acción
                    time_action_frame = tk.Frame(inner_frame, bg=theme["bg_secondary"])
                    time_action_frame.pack(fill="x", pady=(0, 5))
                    
                    timestamp = activity.get("timestamp", "")
                    time_str = self._format_time(timestamp)
                    
                    tk.Label(
                        time_action_frame,
                        text=time_str,
                        font=("Segoe UI", 9),
                        bg=theme["bg_secondary"],
                        fg=theme["text_secondary"],
                        width=10
                    ).pack(side="left")
                    
                    # Icono según tipo de acción
                    action_type = activity.get("action_type", "")
                    icon = self._get_action_icon(action_type)
                    
                    tk.Label(
                        time_action_frame,
                        text=icon,
                        font=("Segoe UI", 12),
                        bg=theme["bg_secondary"],
                        fg=theme["text_primary"]
                    ).pack(side="left", padx=(10, 5))
                    
                    # Descripción
                    description = activity.get("description", "Sin descripción")
                    tk.Label(
                        time_action_frame,
                        text=description,
                        font=("Segoe UI", 9),
                        bg=theme["bg_secondary"],
                        fg=theme["text_primary"],
                        anchor="w"
                    ).pack(side="left", fill="x", expand=True)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Botón cerrar (fuera del scroll_frame para que siempre sea visible)
        close_btn = tk.Button(
            main_frame,
            text="Cerrar",
            font=("Segoe UI", 10, "bold"),
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            relief="solid",
            bd=1,
            padx=20,
            pady=8,
            cursor="hand2",
            command=activity_window.destroy
        )
        close_btn.pack(pady=(0, 0), side="bottom")
    
    def _is_today(self, iso_string):
        """Verifica si una fecha es de hoy"""
        if not iso_string:
            return False
        try:
            from datetime import datetime, date
            dt = datetime.fromisoformat(iso_string)
            return dt.date() == date.today()
        except:
            return False
    
    def _get_date_key(self, iso_string):
        """Obtiene la clave de fecha para agrupar actividades"""
        if not iso_string:
            return "Sin fecha"
        try:
            from datetime import datetime, date
            dt = datetime.fromisoformat(iso_string)
            today = date.today()
            activity_date = dt.date()
            
            if activity_date == today:
                return "Hoy"
            elif activity_date == today.replace(day=today.day - 1):
                return "Ayer"
            else:
                return dt.strftime("%d/%m/%Y")
        except:
            return "Sin fecha"
    
    def _format_time(self, iso_string):
        """Formatea solo la hora de una fecha ISO"""
        if not iso_string:
            return "N/A"
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%H:%M")
        except:
            return "N/A"
    
    def _get_action_icon(self, action_type):
        """Obtiene el icono según el tipo de acción"""
        icons = {
            "user_created": "👤",
            "user_updated": "✏️",
            "user_deleted": "🗑️",
            "password_changed": "🔐",
            "login": "🔓",
            "logout": "🔒",
            "tenant_created": "👥",
            "tenant_updated": "📝",
            "payment_registered": "💰",
            "expense_registered": "💸",
            "apartment_created": "🏠",
            "report_generated": "📊",
            "backup_created": "💾",
            "backup_restored": "🔄"
        }
        return icons.get(action_type, "📋")
    
    def _logout(self):
        """Cierra sesión y sale de la aplicación"""
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar sesión?"):
            self.root.quit()

    def _switch_user(self):
        """Abre el diálogo para cambiar de usuario: selección de usuario activo y contraseña."""
        users = [u for u in self.user_service.get_all_users() if u.get("is_active")]
        if not users:
            messagebox.showwarning("Cambiar Usuario", "No hay usuarios activos en el sistema.")
            return

        win = tk.Toplevel(self.root)
        win.title("Cambiar Usuario")
        win.geometry("340x240")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        theme = theme_manager.themes[theme_manager.current_theme]
        bg = theme.get("bg_secondary", "#ffffff")
        fg = theme.get("text_primary", "#1e293b")
        win.configure(bg=bg)

        # Formulario compacto (sin expand para no dejar hueco)
        form_frame = tk.Frame(win, bg=bg)
        form_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, Spacing.SM))

        tk.Label(form_frame, text="Seleccione el usuario e ingrese la contraseña:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, Spacing.XS))
        tk.Label(form_frame, text="Usuario:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 1))
        display_options = [f"{u.get('full_name', u.get('username', ''))} ({u.get('username', '')})" for u in users]
        usernames = [u.get("username", "") for u in users]
        var_combo = tk.StringVar(value=display_options[0] if display_options else "")
        combo = ttk.Combobox(form_frame, textvariable=var_combo, values=display_options, state="readonly", font=("Segoe UI", 9), width=36)
        combo.pack(fill="x", pady=(0, Spacing.SM))
        combo.current(0)

        tk.Label(form_frame, text="Contraseña:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 1))
        var_pass = tk.StringVar()
        pass_entry = tk.Entry(form_frame, textvariable=var_pass, show="•", font=("Segoe UI", 9), width=38)
        pass_entry.pack(fill="x", pady=(0, 0))
        pass_entry.focus_set()

        def do_login():
            idx = combo.current()
            if idx < 0:
                idx = max(0, display_options.index(var_combo.get())) if var_combo.get() in display_options else 0
            username = usernames[idx] if idx < len(usernames) else usernames[0]
            password = var_pass.get().strip()
            if not password:
                messagebox.showwarning("Cambiar Usuario", "Ingrese la contraseña.", parent=win)
                return
            if not self.user_service.verify_password(username, password):
                messagebox.showerror("Cambiar Usuario", "Contraseña incorrecta.", parent=win)
                return
            user = self.user_service.get_user_by_username(username)
            if user:
                self.current_user = {k: v for k, v in user.items() if k != "password_hash"}
                try:
                    if hasattr(self, "user_btn") and self.user_btn.winfo_exists():
                        name = self.current_user.get("full_name", self.current_user.get("username", "Admin"))
                        self.user_btn.configure(text=f"{Icons.TENANT_PROFILE} {name}")
                except (tk.TclError, AttributeError):
                    pass
            win.destroy()

        def on_cancel():
            win.destroy()

        # Botones compactos en la parte inferior
        btn_frame = tk.Frame(win, bg=bg)
        btn_frame.pack(side="bottom", fill="x", padx=Spacing.MD, pady=Spacing.MD)
        tk.Button(btn_frame, text="Aceptar", font=("Segoe UI", 9), bg="#2563eb", fg="white", relief="flat", bd=0, highlightthickness=0, padx=14, pady=6, cursor="hand2", command=do_login).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btn_frame, text="Cancelar", font=("Segoe UI", 9), bg=theme.get("bg_tertiary", "#e2e8f0"), fg=fg, relief="flat", bd=0, highlightthickness=0, padx=14, pady=6, cursor="hand2", command=on_cancel).pack(side="left")

        win.protocol("WM_DELETE_WINDOW", on_cancel)
    
    def run(self):
        """Ejecuta la aplicación (solo inicia mainloop si esta ventana creó la raíz)."""
        if self._owns_root:
            self.root.mainloop()

    def _check_license_status(self):
        """Revisa estado de demo/licencia y, si ha expirado, muestra diálogo de activación."""
        try:
            from manager.app.services.license_service import license_service
        except Exception:
            return

        status = license_service.get_status()
        mode = status.get("mode")
        remaining = status.get("remaining_days")

        if mode == "demo":
            if remaining is not None and remaining in (15, 7, 3, 1):
                try:
                    messagebox.showinfo(
                        "Licencia",
                        f"Demostración activa. Te quedan {remaining} días de prueba.",
                        parent=self.root,
                    )
                except Exception:
                    pass
            return

        if mode == "expired":
            self._show_license_required_dialog(status)

    def _show_license_activation_dialog(self, title: str, message: str, exit_on_close: bool):
        """Diálogo modal para activar licencia (puede o no forzar salida al cerrar)."""
        try:
            from manager.app.services.license_service import license_service
        except Exception:
            return

        win = tk.Toplevel(self.root)
        win.title("Activación de licencia")
        win.geometry("520x260")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        theme = theme_manager.themes[theme_manager.current_theme]
        bg = theme.get("bg_primary", "#ffffff")
        fg = theme.get("text_primary", "#1e293b")
        fg_sec = theme.get("text_secondary", "#6b7280")
        win.configure(bg=bg)

        content = tk.Frame(win, bg=bg, padx=Spacing.LG, pady=Spacing.LG)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=bg,
            fg=fg,
        ).pack(anchor="w", pady=(0, Spacing.SM))

        tk.Label(
            content,
            text=message,
            font=("Segoe UI", 10),
            bg=bg,
            fg=fg_sec,
            justify="left",
            wraplength=480,
        ).pack(anchor="w", pady=(0, Spacing.MD))

        form = tk.Frame(content, bg=bg)
        form.pack(fill="x", pady=(0, Spacing.MD))

        tk.Label(form, text="Clave de licencia:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w")
        key_var = tk.StringVar()
        entry = tk.Entry(form, textvariable=key_var, font=("Segoe UI", 10))
        entry.pack(fill="x", pady=(2, 0))
        entry.focus_set()

        msg_var = tk.StringVar()
        tk.Label(
            form,
            textvariable=msg_var,
            font=("Segoe UI", 9),
            bg=bg,
            fg="#b91c1c",
            justify="left",
            wraplength=480,
        ).pack(anchor="w", pady=(4, 0))

        btn_frame = tk.Frame(content, bg=bg)
        btn_frame.pack(fill="x", pady=(Spacing.MD, 0))

        btn_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_bg_hover = theme.get("btn_primary_hover", "#1d4ed8")

        def on_activate():
            key = key_var.get().strip()
            result = license_service.validate_key_with_keygen(key)
            if not result.get("ok"):
                msg_var.set(result.get("message", "No se pudo validar la licencia."))
                return
            license_service.activate_license(key, result.get("expires_at"))
            msg_var.set("")
            try:
                messagebox.showinfo(
                    "Licencia activada",
                    "La licencia se ha activado correctamente.",
                    parent=win,
                )
            except Exception:
                pass
            win.destroy()

        def on_close():
            if exit_on_close:
                self.root.destroy()
            else:
                win.destroy()

        btn_activate = tk.Button(
            btn_frame,
            text="Activar licencia",
            font=("Segoe UI", 10),
            bg=btn_bg,
            fg="white",
            activebackground=btn_bg_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=btn_bg,
            highlightcolor=btn_bg,
            padx=16,
            pady=6,
            cursor="hand2",
            command=on_activate,
        )
        btn_activate.pack(side="right", padx=(0, Spacing.SM))
        btn_activate.bind("<Enter>", lambda e: btn_activate.configure(bg=btn_bg_hover))
        btn_activate.bind("<Leave>", lambda e: btn_activate.configure(bg=btn_bg))

        close_text = "Salir" if exit_on_close else "Cancelar"
        btn_close = tk.Button(
            btn_frame,
            text=close_text,
            font=("Segoe UI", 10),
            bg=theme.get("bg_tertiary", "#e5e7eb"),
            fg=fg,
            activebackground="#d1d5db",
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=on_close,
        )
        btn_close.pack(side="right")

        win.protocol("WM_DELETE_WINDOW", on_close)

    def _show_license_details_dialog(self):
        """Muestra detalles del estado de licencia/demo y permite activar."""
        try:
            from manager.app.services.license_service import license_service
        except Exception:
            return

        st = license_service.get_status()
        mode = st.get("mode")
        remaining = st.get("remaining_days")
        demo_ends = st.get("demo_ends_at")
        lic_expires = st.get("license_expires_at")
        lic_key = (st.get("license_key") or "").strip()

        def _fmt_dt(dt):
            try:
                return dt.strftime("%d/%m/%Y")
            except Exception:
                return "N/A"

        if mode == "licensed":
            status_line = f"Estado: Licencia activa (vence el {_fmt_dt(lic_expires)})."
            details_lines = [f"Vencimiento: {_fmt_dt(lic_expires)}"]
        elif mode == "demo":
            status_line = f"Estado: Demostración activa (te quedan {remaining} días)."
            details_lines = [f"Fin de demo: {_fmt_dt(demo_ends)}"]
        else:
            status_line = "Estado: Demostración vencida o licencia expirada."
            details_lines = []

        if lic_key:
            tail = lic_key[-6:]
            details_lines.append(f"Clave: ••••••-{tail}")

        win = tk.Toplevel(self.root)
        win.title("Detalles de licencia")
        win.geometry("520x260")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        theme = theme_manager.themes[theme_manager.current_theme]
        bg = theme.get("bg_primary", "#ffffff")
        fg = theme.get("text_primary", "#1e293b")
        fg_sec = theme.get("text_secondary", "#6b7280")
        win.configure(bg=bg)

        content = tk.Frame(win, bg=bg, padx=Spacing.LG, pady=Spacing.LG)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="Licencia", font=("Segoe UI", 14, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(0, Spacing.SM))
        tk.Label(content, text=status_line, font=("Segoe UI", 10, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(0, Spacing.XS))

        if details_lines:
            tk.Label(
                content,
                text="\n".join(details_lines),
                font=("Segoe UI", 10),
                bg=bg,
                fg=fg_sec,
                justify="left",
                wraplength=480,
            ).pack(anchor="w", pady=(0, Spacing.MD))
        else:
            tk.Label(
                content,
                text="No hay información adicional disponible.",
                font=("Segoe UI", 10),
                bg=bg,
                fg=fg_sec,
            ).pack(anchor="w", pady=(0, Spacing.MD))

        btns = tk.Frame(content, bg=bg)
        btns.pack(fill="x", pady=(Spacing.MD, 0))

        def open_activate():
            win.destroy()
            self._show_license_activation_dialog(
                title="Activar licencia",
                message="Ingrese su clave de licencia anual para activar el software.",
                exit_on_close=False,
            )

        btn_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_bg_hover = theme.get("btn_primary_hover", "#1d4ed8")

        btn_activate = tk.Button(
            btns,
            text="Activar licencia",
            font=("Segoe UI", 10),
            bg=btn_bg,
            fg="white",
            activebackground=btn_bg_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=btn_bg,
            highlightcolor=btn_bg,
            padx=16,
            pady=6,
            cursor="hand2",
            command=open_activate,
        )
        btn_activate.pack(side="right")
        btn_activate.bind("<Enter>", lambda e: btn_activate.configure(bg=btn_bg_hover))
        btn_activate.bind("<Leave>", lambda e: btn_activate.configure(bg=btn_bg))

        tk.Button(
            btns,
            text="Cerrar",
            font=("Segoe UI", 10),
            bg=theme.get("bg_tertiary", "#e5e7eb"),
            fg=fg,
            activebackground="#d1d5db",
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=win.destroy,
        ).pack(side="right", padx=(0, Spacing.SM))

        win.protocol("WM_DELETE_WINDOW", win.destroy)

    def _show_license_required_dialog(self, status):
        """Diálogo modal para activar licencia cuando la demo ha expirado (bloqueante)."""
        self._show_license_activation_dialog(
            title="Periodo de prueba finalizado",
            message=(
                "Tu periodo de demostración de Building Manager Pro ha finalizado.\n"
                "Para seguir usando la aplicación, activa tu licencia anual introduciendo la clave "
                "de activación que recibiste al comprar."
            ),
            exit_on_close=True,
        )

    def _maybe_show_onboarding(self):
        """Muestra el diálogo de bienvenida/onboarding solo la primera vez."""
        try:
            from manager.app.services.app_config_service import app_config_service
            if app_config_service.get_onboarding_completed():
                return
        except Exception:
            return

        win = tk.Toplevel(self.root)
        win.title("Bienvenido a Building Manager Pro")
        win.geometry("560x460")
        win.transient(self.root)
        win.grab_set()
        win.resizable(True, True)
        win.minsize(520, 420)

        theme = theme_manager.themes[theme_manager.current_theme]
        bg = theme.get("bg_primary", "#ffffff")
        fg = theme.get("text_primary", "#1e293b")
        fg_sec = theme.get("text_secondary", "#6b7280")
        win.configure(bg=bg)

        # Contenido
        content = tk.Frame(win, bg=bg, padx=Spacing.LG, pady=Spacing.LG)
        content.pack(fill="both", expand=True)

        intro_wraplength = 500
        tk.Label(content, text="Bienvenido al Dashboard", font=("Segoe UI", 18, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(0, Spacing.SM))
        tk.Label(
            content,
            text="Para comenzar, cree su edificio y las unidades (apartamentos, locales, etc.) que lo conforman. "
                 "Una vez hecho esto, podrá gestionar inquilinos, pagos y gastos desde cada módulo del menú.",
            font=("Segoe UI", 10),
            bg=bg,
            fg=fg_sec,
            justify="left",
            wraplength=intro_wraplength,
        ).pack(anchor="w", pady=(0, Spacing.SM))
        tk.Label(
            content,
            text="Para crear el edificio y las unidades, use el módulo Administración del menú lateral "
                 "(opciones «Edificio» y «Unidades»).",
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg=fg,
            justify="left",
            wraplength=intro_wraplength,
        ).pack(anchor="w", pady=(0, Spacing.MD))

        tk.Label(content, text="Módulos principales:", font=("Segoe UI", 11, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(Spacing.MD, Spacing.XS))
        mods = [
            "• Inquilinos: registro y estado de arrendatarios.",
            "• Pagos: cobros y estado de cuentas.",
            "• Gastos: registro de gastos del edificio.",
            "• Administración: edificio, unidades, usuarios y reportes.",
            "• Reportes: informes y exportaciones.",
        ]
        mod_wraplength = 500
        for line in mods:
            tk.Label(content, text=line, font=("Segoe UI", 10), bg=bg, fg=fg_sec, justify="left", wraplength=mod_wraplength).pack(anchor="w")

        def finish():
            try:
                app_config_service.set_onboarding_completed(True)
            except Exception:
                pass
            win.destroy()

        btn_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_frame = tk.Frame(content, bg=bg)
        btn_frame.pack(side="bottom", pady=(Spacing.LG, 0))
        tk.Button(
            btn_frame,
            text="Comenzar",
            font=("Segoe UI", 10),
            bg=btn_bg,
            fg="white",
            activebackground=btn_bg,
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=btn_bg,
            highlightcolor=btn_bg,
            padx=18,
            pady=8,
            cursor="hand2",
            command=finish,
        ).pack()

        win.protocol("WM_DELETE_WINDOW", finish)
