"""
Vista principal del módulo de inquilinos - Diseño rediseñado
Sistema simplificado con 4 opciones principales para el administrador
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.services.tenant_service import tenant_service
from manager.app.ui.views.tenant_form_view import TenantFormView
from manager.app.ui.views.tenant_details_view import TenantDetailsView
from manager.app.ui.views.edit_delete_tenants_view import EditDeleteTenantsView
import csv
import os

class TenantsView(tk.Frame):
    """Vista principal del módulo de inquilinos con diseño simplificado"""
    
    def __init__(self, parent, on_navigate: Callable = None, on_data_change: Callable = None, on_register_payment: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_navigate = on_navigate
        self.on_data_change = on_data_change
        self.on_register_payment_callback = on_register_payment
        self.current_view = "dashboard"
        self.selected_tenant = None
        
        # Crear layout principal
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal con 4 cards centrales"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Título principal
        title_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        title_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Botón volver - movido al lado derecho
        btn_back = tk.Button(
            title_frame,
            text="← Volver al Menú",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._on_back_clicked
        )
        btn_back.pack(side="right")
        
        # Pregunta principal
        question_label = tk.Label(
            self,
            text="¿Qué deseas hacer?",
            **theme_manager.get_style("label_subtitle")
        )
        question_label.configure(font=("Segoe UI", 14))
        question_label.pack(pady=(0, Spacing.XL))
        
        # Contenedor principal centrado
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(pady=Spacing.LG)
        
        # Grid de cards 2x2 con espaciado optimizado
        self._create_cards_grid(main_container)
    
    def _create_cards_grid(self, parent):
        """Crea el grid de 4 cards principales"""
        # Centrar todo el contenido
        grid_container = tk.Frame(parent, **theme_manager.get_style("frame"))
        grid_container.pack(anchor="center")
        
        # Fila 1
        row1 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row1.pack(pady=(0, Spacing.LG))
        
        # Card 1: Agregar Inquilino
        self._create_action_card(
            row1, 
            "➕", 
            "Agregar Inquilino",
            "Registrar un nuevo inquilino en el sistema",
            "#1e40af",  # primary blue
            lambda: self._show_tenant_form()
        ).pack(side="left", padx=(0, Spacing.LG))
        
        # Card 2: Ver Inquilinos  
        self._create_action_card(
            row1,
            "👥",
            "Ver Inquilinos", 
            "Consultar lista completa de inquilinos",
            "#3b82f6",  # info blue
            lambda: self._show_tenants_list()
        ).pack(side="left")
        
        # Fila 2
        row2 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row2.pack()
        
        # Card 3: Editar/Eliminar
        self._create_action_card(
            row2,
            "✏️", 
            "Editar/Eliminar",
            "Modificar o eliminar inquilinos existentes",
            "#f59e0b",  # warning orange
            lambda: self._show_edit_options()
        ).pack(side="left", padx=(0, Spacing.LG))
        
        # Card 4: Reportes
        self._create_action_card(
            row2,
            "📊",
            "Reportes", 
            "Generar reportes y estadísticas",
            "#10b981",  # success green
            lambda: self._show_reports()
        ).pack(side="left")
    
    def _create_action_card(self, parent, icon, title, description, color, command):
        """Crea una card de acción con hover effects estilo módulo pagos"""
        card_frame = tk.Frame(
            parent,
            bg="white",
            relief="raised",
            bd=2,
            width=260,
            height=220
        )
        card_frame.pack_propagate(False)
        content_frame = tk.Frame(card_frame, bg="white")
        content_frame.pack(fill="both", expand=True)
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=("Segoe UI", 28),
            bg="white",
            fg=color
        )
        icon_label.pack(pady=(0, Spacing.MD))
        title_label = tk.Label(
            content_frame,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=color
        )
        title_label.pack()
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=("Segoe UI", 10),
            bg="white",
            fg="#444",
            wraplength=200,
            justify="center"
        )
        desc_label.pack(pady=(Spacing.XS, 0))
        def on_enter(event):
            card_frame.configure(bg="#e3f2fd")
            content_frame.configure(bg="#e3f2fd")
            icon_label.configure(bg="#e3f2fd")
            title_label.configure(bg="#e3f2fd")
            desc_label.configure(bg="#e3f2fd")
        def on_leave(event):
            card_frame.configure(bg="white")
            content_frame.configure(bg="white")
            icon_label.configure(bg="white")
            title_label.configure(bg="white")
            desc_label.configure(bg="white")
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        for w in [icon_label, title_label, desc_label]:
            w.bind("<Button-1>", lambda e: command())
            w.configure(cursor="hand2")
        card_frame.bind("<Button-1>", lambda e: command())
        card_frame.configure(cursor="hand2")
        return card_frame
    
    def _show_tenant_form(self):
        """Muestra el formulario de nuevo inquilino"""
        self.current_view = "form"
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Crear formulario
        form_view = TenantFormView(
            self,
            on_back=self._back_to_dashboard,
            on_save_success=self.on_data_change
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_tenants_list(self):
        """VERSIÓN COMPLETA - Sistema avanzado de gestión de inquilinos"""
        self.current_view = "list"
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        # =================== HEADER ===================
        header_frame = tk.Frame(self, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(0, 15))
        title_label = tk.Label(
            header_frame,
            text="👁️ Ver detalles inquilinos",
            font=("Segoe UI", 18, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        title_label.pack(side="left", padx=10)
        btn_back = tk.Button(
            header_frame,
            text="← Volver al Menú",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            relief="flat",
            padx=15,
            command=self._back_to_dashboard
        )
        btn_back.pack(side="right", padx=10)
        # =================== CONTAINER PRINCIPAL ===================
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        # =================== PANEL BÚSQUEDA (30%) ===================
        search_panel = self._create_search_panel(main_container)
        search_panel.pack(side="left", fill="y", padx=(0, 15))
        # =================== PANEL LISTA (70%) ===================
        list_panel = self._create_list_panel(main_container)
        list_panel.pack(side="right", fill="both", expand=True)
        # =================== CARGAR DATOS ===================
        self._load_and_display_tenants()
    
    def _create_search_panel(self, parent):
        """Crea el panel de búsqueda avanzada"""
        # Frame principal del panel
        panel = tk.Frame(parent, bg="#e3f2fd", relief="solid", bd=2, width=380, height=420)
        panel.pack_propagate(False)
        panel.grid_propagate(False)
        # Header del panel
        header = tk.Frame(panel, bg="#1976d2", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = tk.Label(
            header,
            text="🔍 Búsqueda Avanzada",
            font=("Segoe UI", 12, "bold"),
            bg="#1976d2",
            fg="white"
        )
        title.pack(expand=True)
        # Contenido del panel
        content = tk.Frame(panel, bg="#e3f2fd")
        content.pack(fill="both", expand=True, padx=12, pady=12)
        
        # === BÚSQUEDA POR TEXTO ===
        tk.Label(content, text="Búsqueda general:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,2))
        tk.Label(content, text="(Nombre, Cédula, Apartamento, Email, Teléfono)", font=("Segoe UI", 8), bg="#e3f2fd", fg="#666666").pack(anchor="w", pady=(0,5))
        self.search_entry = tk.Entry(content, font=("Segoe UI", 10), relief="solid", bd=1)
        self.search_entry.pack(fill="x", pady=(0,10))
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        
        # === FILTRO POR APARTAMENTO ===
        tk.Label(content, text="Filtro por apartamento:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,5))
        self.apartment_var = tk.StringVar(value="Todos")
        apartment_combo = ttk.Combobox(content, textvariable=self.apartment_var, font=("Segoe UI", 10))
        apartment_combo['values'] = ("Todos", "101", "102", "103", "106", "201", "202", "203", "301", "302", "303")
        apartment_combo.pack(fill="x", pady=(0,10))
        apartment_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # === FILTRO POR ESTADO ===
        tk.Label(content, text="Estado:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,5))
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(content, textvariable=self.status_var, font=("Segoe UI", 10))
        status_combo['values'] = ("Todos", "Activo", "En Mora", "Inactivo")
        status_combo.pack(fill="x", pady=(0,10))
        status_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # === RANGO DE FECHAS (COMPACTO) ===
        tk.Label(content, text="Fecha de ingreso:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(5,2))
        
        date_frame = tk.Frame(content, bg="#e3f2fd")
        date_frame.pack(fill="x", pady=(0,5))
        
        tk.Label(date_frame, text="Desde:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.date_from = tk.Entry(date_frame, width=10, font=("Segoe UI", 8))
        self.date_from.pack(side="left", padx=(3,8))
        
        tk.Label(date_frame, text="Hasta:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.date_to = tk.Entry(date_frame, width=10, font=("Segoe UI", 8))
        self.date_to.pack(side="left", padx=3)
        
        # === RANGO DE ARRIENDO (COMPACTO) ===
        tk.Label(content, text="Rango de arriendo:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(5,2))
        
        rent_frame = tk.Frame(content, bg="#e3f2fd")
        rent_frame.pack(fill="x", pady=(0,5))
        
        tk.Label(rent_frame, text="Min:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.rent_min = tk.Entry(rent_frame, width=8, font=("Segoe UI", 8))
        self.rent_min.pack(side="left", padx=(3,8))
        
        tk.Label(rent_frame, text="Max:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.rent_max = tk.Entry(rent_frame, width=8, font=("Segoe UI", 8))
        self.rent_max.pack(side="left", padx=3)
        
        # === INDICADOR DE RESULTADOS ===
        self.results_indicator = tk.Label(
            content,
            text="📊 Resultados: mostrando todos",
            font=("Segoe UI", 8),
            bg="#e3f2fd",
            fg="#2e7d32"
        )
        self.results_indicator.pack(anchor="w", pady=(8,8))
        
        # === BOTONES ===
        btn_frame = tk.Frame(content, bg="#e3f2fd")
        btn_frame.pack(fill="x", pady=8)
        
        btn_search = tk.Button(
            btn_frame,
            text="🔍 Aplicar",
            font=("Segoe UI", 9, "bold"),
            bg="#4caf50",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=self._apply_filters
        )
        btn_search.pack(side="left", padx=(0,8))
        
        btn_clear = tk.Button(
            btn_frame,
            text="🧹 Limpiar",
            font=("Segoe UI", 9),
            bg="#ff9800",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=self._clear_filters
        )
        btn_clear.pack(side="left")
        
        return panel
    
    def _create_list_panel(self, parent):
        """Crea el panel de lista de inquilinos"""
        panel = tk.Frame(parent, bg="#f1f8e9", relief="solid", bd=2)
        header = tk.Frame(panel, bg="#388e3c", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        header_content = tk.Frame(header, bg="#388e3c")
        header_content.pack(expand=True)
        self.list_title = tk.Label(
            header_content,
            text="📋 Lista de Inquilinos",
            font=("Segoe UI", 12, "bold"),
            bg="#388e3c",
            fg="white"
        )
        self.list_title.pack(side="left", padx=15)
        self.counter_label = tk.Label(
            header_content,
            text="(0 inquilinos)",
            font=("Segoe UI", 10),
            bg="#388e3c",
            fg="#c8e6c9"
        )
        self.counter_label.pack(side="left", padx=5)
        # Botón exportar
        btn_export = tk.Button(
            header_content,
            text="📊 Exportar",
            font=("Segoe UI", 9),
            bg="#2e7d32",
            fg="white",
            relief="flat",
            padx=15,
            command=self._export_list
        )
        btn_export.pack(side="right", padx=15)
        self.scroll_frame = tk.Frame(panel, bg="#f1f8e9")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.scroll_frame, bg="#f1f8e9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f1f8e9")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return panel
    
    def _load_and_display_tenants(self):
        """Carga y muestra todos los inquilinos con agrupación inteligente"""
        try:
            tenants = tenant_service.get_all_tenants()
            self.all_tenants = tenants  # Guardar para filtros
            self._display_tenants(tenants)
            
        except Exception as e:
            self._show_error(f"Error al cargar inquilinos: {str(e)}")
    
    def _display_tenants(self, tenants):
        """Muestra los inquilinos agrupados por estado"""
        # Limpiar contenido anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not tenants:
            self._show_empty_state()
            return
        
        # Agrupar por estado (real)
        active_tenants = []
        overdue_tenants = []
        inactive_tenants = []
        
        for tenant in tenants:
            estado = tenant.get('estado_pago', 'al_dia')
            if estado == 'inactivo':
                inactive_tenants.append(tenant)
            elif estado == 'moroso':
                overdue_tenants.append(tenant)
            else:
                active_tenants.append(tenant)
        
        # Mostrar grupos
        current_row = 0
        
        if active_tenants:
            current_row = self._display_group("✅ ACTIVOS", active_tenants, "#4caf50", current_row)
        
        if overdue_tenants:
            current_row = self._display_group("⚠️ EN MORA", overdue_tenants, "#ff9800", current_row)
        
        if inactive_tenants:
            current_row = self._display_group("❌ INACTIVOS", inactive_tenants, "#f44336", current_row)
        
        # Actualizar contador
        total = len(tenants)
        self.counter_label.config(text=f"({total} inquilino{'s' if total != 1 else ''})")
        
        # Actualizar indicador de resultados en el panel de búsqueda
        if hasattr(self, 'results_indicator'):
            total_available = len(getattr(self, 'all_tenants', []))
            if total == total_available:
                self.results_indicator.config(
                    text="📊 Resultados: mostrando todos",
                    fg="#2e7d32"
                )
            else:
                self.results_indicator.config(
                    text=f"🔍 Resultados: {total} de {total_available} inquilinos",
                    fg="#1976d2"
                )
        
        # Forzar actualización del scroll
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _display_group(self, title, tenants, color, start_row):
        """Muestra un grupo de inquilinos"""
        # Separador y título del grupo
        separator = tk.Frame(self.scrollable_frame, bg=color, height=2)
        separator.pack(fill="x", pady=(10,0))
        
        group_title = tk.Label(
            self.scrollable_frame,
            text=f"{title} ({len(tenants)})",
            font=("Segoe UI", 11, "bold"),
            bg="#f1f8e9",
            fg=color
        )
        group_title.pack(anchor="w", pady=(5,5))
        
        # Inquilinos del grupo
        for i, tenant in enumerate(tenants):
            self._create_tenant_row(tenant, color, i % 2 == 0)
        
        return start_row + len(tenants)
    
    def _create_tenant_row(self, tenant, status_color, is_even):
        """Crea una fila para un inquilino con información completa y clic"""
        bg_color = "#ffffff" if is_even else "#f8f9fa"
        row_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief="solid", bd=1)
        row_frame.pack(fill="x", pady=1)
        content = tk.Frame(row_frame, bg=bg_color)
        content.pack(fill="x", padx=10, pady=8)
        name = tenant.get('nombre', 'Sin nombre')
        apartment = tenant.get('apartamento', 'N/A')
        valor_arriendo = tenant.get('valor_arriendo', 0)
        estado_pago = tenant.get('estado_pago', 'al_dia')
        estado_texto = {
            'al_dia': 'Al día',
            'moroso': 'En mora',
            'inactivo': 'Inactivo'
        }.get(estado_pago, 'Al día')
        main_info = tk.Label(
            content,
            text=f"👤 {name}",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            anchor="w"
        )
        main_info.pack(anchor="w")
        details = tk.Label(
            content,
            text=f"🏠 Apartamento: {apartment} | 💰 Arriendo: ${valor_arriendo:,.0f} | 📞 Teléfono: {tenant.get('telefono', 'No registrado')}",
            font=("Segoe UI", 9),
            bg=bg_color,
            anchor="w"
        )
        details.pack(anchor="w", pady=(2,0))
        # Día de pago (si existe fecha_ingreso)
        fecha_ingreso = tenant.get('fecha_ingreso', None)
        dia_pago = None
        if fecha_ingreso:
            try:
                # Suponiendo formato DD/MM/YYYY o similar
                dia_pago = int(fecha_ingreso.split('/')[0])
            except Exception:
                dia_pago = None
        if dia_pago:
            dia_pago_label = tk.Label(
                content,
                text=f"📅 Día de pago: {dia_pago} de cada mes",
                font=("Segoe UI", 9),
                bg=bg_color,
                fg="#1976d2",
                anchor="w"
            )
            dia_pago_label.pack(anchor="w")
        estado_label = tk.Label(
            content,
            text=f"● {estado_texto}",
            font=("Segoe UI", 9, "bold"),
            fg=status_color,
            bg=bg_color
        )
        estado_label.pack(anchor="w", pady=(2,0))
        # Hacer clic en el card para ver detalles
        def on_card_click(event, t=tenant):
            self._show_tenant_details(t)
        # Bind a todo el card y sus hijos
        for widget in [row_frame, content, main_info, details, estado_label]:
            widget.bind("<Button-1>", on_card_click)
            widget.configure(cursor="hand2")
        if 'dia_pago_label' in locals():
            dia_pago_label.bind("<Button-1>", on_card_click)
            dia_pago_label.configure(cursor="hand2")
    
    def _show_tenant_details(self, tenant):
        """Muestra los detalles de un inquilino"""
        self.current_view = "details"
        self.selected_tenant = tenant
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        # Crear vista de detalles con callback explícito para registrar pago
        details_view = TenantDetailsView(
            self,
            tenant_data=tenant,
            on_back=self._back_to_list,
            on_edit=self._edit_tenant,
            on_register_payment=self.on_register_payment_callback
        )
        details_view.pack(fill="both", expand=True)
    
    def _edit_tenant(self, tenant):
        """Edita un inquilino"""
        self.current_view = "edit"
        self.selected_tenant = tenant
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Crear formulario de edición
        form_view = TenantFormView(
            self,
            on_back=self._back_to_list,
            tenant_data=tenant,
            on_save_success=self.on_data_change
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_edit_options(self):
        """Muestra la vista independiente de Editar/Eliminar Inquilinos"""
        self.current_view = "edit_delete"
        for widget in self.winfo_children():
            widget.destroy()
        edit_delete_view = EditDeleteTenantsView(self, on_navigate=self.on_navigate, on_data_change=self.on_data_change)
        edit_delete_view.pack(fill="both", expand=True)
    
    def _show_reports(self):
        """Muestra reportes"""
        messagebox.showinfo(
            "Reportes",
            "Módulo de reportes en desarrollo.\n\n" +
            "Próximamente disponible:\n" +
            "• Reporte de ocupación\n" +
            "• Reporte de pagos\n" +
            "• Estadísticas generales"
        )
    
    def _back_to_dashboard(self):
        """Vuelve al dashboard principal"""
        self.current_view = "dashboard"
        self._create_layout()
    
    def _back_to_list(self):
        """Vuelve a la lista de inquilinos"""
        self._show_tenants_list()
    
    def _on_back_clicked(self):
        """Maneja el clic en volver al menú principal"""
        if self.on_navigate:
            self.on_navigate("dashboard")

    def _on_search_change(self, event=None):
        """Búsqueda en tiempo real"""
        self._apply_filters()

    def _on_filter_change(self, event=None):
        """Aplicar filtros cuando cambian los combos"""
        self._apply_filters()

    def _apply_filters(self):
        """Aplica todos los filtros activos"""
        if not hasattr(self, 'all_tenants'):
            return
        filtered = self.all_tenants.copy()
        # Filtro por texto - BÚSQUEDA MEJORADA
        search_text = self.search_entry.get().lower().strip()
        if search_text:
            filtered = [t for t in filtered if 
                       search_text in t.get('nombre', '').lower() or
                       search_text in t.get('numero_documento', '').lower() or
                       search_text in t.get('apartamento', '').lower() or
                       search_text in t.get('email', '').lower() or
                       search_text in t.get('telefono', '').lower()]
        # Filtro por apartamento (combo) - Solo aplica si no se buscó apartamento en texto
        apartment = self.apartment_var.get()
        if apartment != "Todos" and not search_text:
            filtered = [t for t in filtered if t.get('apartamento') == apartment]
        elif apartment != "Todos" and search_text:
            filtered = [t for t in filtered if t.get('apartamento') == apartment]
        # Filtro por estado
        status = self.status_var.get()
        if status != "Todos":
            status_mapping = {
                "Activo": "al_dia",
                "En Mora": "moroso",
                "Inactivo": "inactivo"
            }
            target_status = status_mapping.get(status, status.lower())
            filtered = [t for t in filtered if t.get('estado_pago') == target_status]
        self._display_tenants(filtered)

    def _clear_filters(self):
        """Limpia todos los filtros"""
        self.search_entry.delete(0, tk.END)
        self.apartment_var.set("Todos")
        self.status_var.set("Todos")
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.rent_min.delete(0, tk.END)
        self.rent_max.delete(0, tk.END)
        if hasattr(self, 'all_tenants'):
            self._display_tenants(self.all_tenants)

    def _confirm_delete_tenant(self, tenant):
        nombre = tenant.get("nombre", "Inquilino")
        if messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas eliminar a {nombre}? Esta acción no se puede deshacer."):
            success = tenant_service.delete_tenant(tenant.get("id"))
            if success:
                self._load_and_display_tenants()
                messagebox.showinfo("Eliminado", f"Inquilino '{nombre}' eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el inquilino.")

    def _export_list(self):
        """Exportar la lista de inquilinos filtrados a CSV en la carpeta exports con columnas legibles"""
        tenants = getattr(self, 'filtered_tenants', None)
        if tenants is None:
            tenants = getattr(self, 'all_tenants', [])
        if not tenants:
            messagebox.showwarning("Exportar", "No hay inquilinos para exportar.")
            return
        # Encabezados legibles
        headers = [
            ("ID", "id"),
            ("Nombre", "nombre"),
            ("Documento", "numero_documento"),
            ("Teléfono", "telefono"),
            ("Email", "email"),
            ("Apartamento", "apartamento"),
            ("Valor Arriendo", "valor_arriendo"),
            ("Fecha de Ingreso", "fecha_ingreso"),
            ("Estado de Pago", "estado_pago"),
            ("Dirección", "direccion"),
            ("Contacto Emergencia", "contacto_emergencia_nombre"),
            ("Teléfono Emergencia", "contacto_emergencia_telefono")
        ]
        # Crear carpeta exports si no existe
        export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../exports'))
        os.makedirs(export_dir, exist_ok=True)
        ruta = os.path.join(export_dir, "inquilinos_exportados.csv")
        try:
            with open(ruta, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([h[0] for h in headers])
                for t in tenants:
                    row = [t.get(h[1], "") for h in headers]
                    writer.writerow(row)
            messagebox.showinfo("Exportar", f"Exportación exitosa. Archivo guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Exportar", f"Error al exportar: {str(e)}")

    def on_register_payment(self, tenant):
        # Llama a la función de navegación real si está disponible
        if self.on_register_payment_callback:
            self.on_register_payment_callback(tenant)
            return
        from tkinter import messagebox
        messagebox.showinfo("Navegación", "No se pudo navegar al módulo de pagos.")