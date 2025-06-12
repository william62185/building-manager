"""
Vista principal del módulo de inquilinos - Diseño rediseñado
Sistema simplificado con 4 opciones principales para el administrador
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional
from app.ui.components.theme_manager import theme_manager, Spacing
from app.ui.components.icons import Icons
from app.services.tenant_service import tenant_service
from app.ui.views.tenant_form_view import TenantFormView
from app.ui.views.tenant_details_view import TenantDetailsView

class TenantsView(tk.Frame):
    """Vista principal del módulo de inquilinos con diseño simplificado"""
    
    def __init__(self, parent, on_navigate: Callable = None, on_data_change: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_navigate = on_navigate
        self.on_data_change = on_data_change
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
        """Crea una card de acción con hover effects"""
        # Frame principal de la card con dimensiones optimizadas
        card_frame = tk.Frame(
            parent,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            relief="solid",
            bd=1,
            width=280,  # Ancho reducido
            height=180   # Alto reducido
        )
        card_frame.pack_propagate(False)  # Mantener dimensiones fijas
        
        # Contenido de la card
        content_frame = tk.Frame(card_frame, bg=card_frame["bg"])
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icono grande
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=("Segoe UI", 24),
            bg=card_frame["bg"],
            fg=color
        )
        icon_label.pack(pady=(0, Spacing.MD))
        
        # Título
        title_label = tk.Label(
            content_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=card_frame["bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        title_label.pack()
        
        # Descripción con wrap optimizado
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=("Segoe UI", 9),
            bg=card_frame["bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"],
            wraplength=240,  # Ancho de wrap ajustado
            justify="center"
        )
        desc_label.pack(pady=(Spacing.XS, 0))
        
        # Efectos hover
        def on_enter(event):
            card_frame.configure(
                bg=color,
                relief="solid",
                bd=2
            )
            content_frame.configure(bg=color)
            icon_label.configure(bg=color, fg="white")
            title_label.configure(bg=color, fg="white")
            desc_label.configure(bg=color, fg="white")
            
        def on_leave(event):
            original_bg = theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            card_frame.configure(
                bg=original_bg,
                relief="solid", 
                bd=1
            )
            content_frame.configure(bg=original_bg)
            icon_label.configure(bg=original_bg, fg=color)
            title_label.configure(bg=original_bg, fg=theme_manager.themes[theme_manager.current_theme]["text_primary"])
            desc_label.configure(bg=original_bg, fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"])
        
        def on_click(event):
            command()
            
        # Bind events a todos los elementos
        for widget in [card_frame, content_frame, icon_label, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            widget.configure(cursor="hand2")
        
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
        panel = tk.Frame(parent, bg="#e3f2fd", relief="solid", bd=2, width=380)
        panel.pack_propagate(False)
        
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
        # Frame principal del panel
        panel = tk.Frame(parent, bg="#f1f8e9", relief="solid", bd=2)
        
        # Header del panel con contador
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
        
        # Área scrolleable para la lista
        self.scroll_frame = tk.Frame(panel, bg="#f1f8e9")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar para scroll MEJORADO
        self.canvas = tk.Canvas(self.scroll_frame, bg="#f1f8e9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f1f8e9")
        
        # Configurar scroll con eventos
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Habilitar scroll con mouse wheel
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind del mouse wheel cuando el mouse entra/sale del canvas
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
        
        # Agrupar por estado (simulado)
        active_tenants = []
        overdue_tenants = []
        inactive_tenants = []
        
        for tenant in tenants:
            # Simulamos estados para demostración
            name = tenant.get('nombre', 'Sin nombre')
            if 'Carlos' in name or 'María' in name:
                overdue_tenants.append(tenant)
            elif 'Ana' in name:
                inactive_tenants.append(tenant)
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
        
        row_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief="solid", bd=1, cursor="hand2")
        row_frame.pack(fill="x", pady=1)
        
        # Contenido de la fila
        content = tk.Frame(row_frame, bg=bg_color)
        content.pack(fill="x", padx=10, pady=8)
        
        # Nombre y apartamento
        name = tenant.get('nombre', 'Sin nombre')
        apartment = tenant.get('apartamento', 'N/A')
        valor_arriendo = tenant.get('valor_arriendo', 0)
        estado_pago = tenant.get('estado_pago', 'al_dia')
        
        # Calcular información de mora si es necesario
        mora_info = self._calculate_mora_info(tenant)
        
        # Mapear estado a texto legible
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
        
        # Información del apartamento y arriendo
        details = tk.Label(
            content,
            text=f"🏠 Apartamento: {apartment} | 💰 Arriendo: ${valor_arriendo:,.0f} | 📞 Teléfono: {tenant.get('telefono', 'No registrado')}",
            font=("Segoe UI", 9),
            bg=bg_color,
            fg="#666666",
            anchor="w"
        )
        details.pack(anchor="w")
        
        # Badge de estado con texto
        badge_frame = tk.Frame(content, bg=bg_color)
        badge_frame.pack(anchor="w", pady=(5,0))
        
        status_badge = tk.Label(
            badge_frame,
            text="●",
            font=("Segoe UI", 12),
            bg=bg_color,
            fg=status_color
        )
        status_badge.pack(side="left")
        
        status_text = tk.Label(
            badge_frame,
            text=estado_texto,
            font=("Segoe UI", 9, "bold"),
            bg=bg_color,
            fg=status_color
        )
        status_text.pack(side="left", padx=(3, 0))
        
        # Información adicional de mora si aplica
        if estado_pago == 'moroso' and mora_info:
            # Color y formato para morosos
            color_mora = "#dc2626"  # Rojo para moroso
            icono_mora = "⚠️"
            
            mora_details = tk.Label(
                content,
                text=f"{icono_mora} {mora_info['dias_mora']} días en mora | 💳 Debe: ${mora_info['valor_mora']:,.0f}",
                font=("Segoe UI", 9, "bold"),
                bg=bg_color,
                fg=color_mora,
                anchor="w"
            )
            mora_details.pack(anchor="w", pady=(2, 0))
        
        # Efectos hover
        def on_enter(e):
            row_frame.config(bg="#e8f5e8")
            content.config(bg="#e8f5e8")
            main_info.config(bg="#e8f5e8")
            details.config(bg="#e8f5e8")
            badge_frame.config(bg="#e8f5e8")
            status_badge.config(bg="#e8f5e8")
            status_text.config(bg="#e8f5e8")
            if estado_pago == 'moroso' and mora_info:
                mora_details.config(bg="#e8f5e8")
        
        def on_leave(e):
            row_frame.config(bg=bg_color)
            content.config(bg=bg_color)
            main_info.config(bg=bg_color)
            details.config(bg=bg_color)
            badge_frame.config(bg=bg_color)
            status_badge.config(bg=bg_color)
            status_text.config(bg=bg_color)
            if estado_pago == 'moroso' and mora_info:
                mora_details.config(bg=bg_color)
        
        # Función de clic para mostrar detalles
        def on_click(e):
            self._show_tenant_details(tenant)
        
        # Bind eventos a todos los widgets
        widgets_to_bind = [row_frame, content, main_info, details, badge_frame, status_badge, status_text]
        
        # Agregar mora_details a los widgets si existe
        if estado_pago == 'moroso' and mora_info:
            widgets_to_bind.append(mora_details)
        
        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            widget.configure(cursor="hand2")
    
    def _calculate_mora_info(self, tenant):
        """Calcula información de mora para un inquilino"""
        estado_pago = tenant.get('estado_pago', 'al_dia')
        
        if estado_pago != 'moroso':
            return None
        
        # Simular cálculo de días en mora basado en el ID del inquilino
        # En una implementación real, esto se basaría en fechas de último pago
        tenant_id = tenant.get('id', 1)
        
        # Datos simulados pero realistas para morosos
        # Para morosos, entre 30-90 días de mora
        dias_mora = 30 + (tenant_id * 7) % 60  # Entre 30-90 días
        # Valor en mora: puede ser 1-3 meses de arriendo
        meses_mora = 1 + (tenant_id % 3)  # 1-3 meses
        
        valor_arriendo = tenant.get('valor_arriendo', 0)
        valor_mora = valor_arriendo * meses_mora
        
        return {
            'dias_mora': dias_mora,
            'valor_mora': valor_mora,
            'meses_mora': meses_mora
        }
    
    def _show_empty_state(self):
        """Muestra estado vacío cuando no hay inquilinos"""
        empty_frame = tk.Frame(self.scrollable_frame, bg="#f1f8e9")
        empty_frame.pack(expand=True, fill="both", pady=50)
        
        tk.Label(
            empty_frame,
            text="📭",
            font=("Segoe UI", 48),
            bg="#f1f8e9"
        ).pack()
        
        tk.Label(
            empty_frame,
            text="No se encontraron inquilinos",
            font=("Segoe UI", 14, "bold"),
            bg="#f1f8e9",
            fg="#666666"
        ).pack(pady=(10,5))
        
        tk.Label(
            empty_frame,
            text="Ajusta los filtros de búsqueda o registra nuevos inquilinos",
            font=("Segoe UI", 10),
            bg="#f1f8e9",
            fg="#999999"
        ).pack()
    
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
            # Si hay búsqueda de texto Y filtro de apartamento, aplicar ambos
            filtered = [t for t in filtered if t.get('apartamento') == apartment]
        
        # Filtro por estado
        status = self.status_var.get()
        if status != "Todos":
            # Mapear estado de la UI al estado real en los datos
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
    
    def _export_list(self):
        """Exporta la lista actual"""
        # Aquí implementarías la funcionalidad de exportación
        messagebox.showinfo("Exportar", "Funcionalidad de exportación implementada próximamente")
    
    def _show_error(self, message):
        """Muestra un mensaje de error"""
        error_frame = tk.Frame(self.scrollable_frame, bg="#f1f8e9")
        error_frame.pack(expand=True, fill="both", pady=50)
        
        tk.Label(
            error_frame,
            text="⚠️",
            font=("Segoe UI", 48),
            bg="#f1f8e9",
            fg="#f44336"
        ).pack()
        
        tk.Label(
            error_frame,
            text="Error al cargar datos",
            font=("Segoe UI", 14, "bold"),
            bg="#f1f8e9",
            fg="#f44336"
        ).pack(pady=(10,5))
        
        tk.Label(
            error_frame,
            text=message,
            font=("Segoe UI", 10),
            bg="#f1f8e9",
            fg="#666666"
        ).pack()
    
    def _show_tenant_details(self, tenant):
        """Muestra los detalles de un inquilino"""
        self.current_view = "details"
        self.selected_tenant = tenant
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Crear vista de detalles
        details_view = TenantDetailsView(
            self,
            tenant_data=tenant,
            on_back=self._back_to_list,
            on_edit=self._edit_tenant
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
        """Muestra opciones de edición/eliminación"""
        messagebox.showinfo(
            "Información",
            "Para editar o eliminar inquilinos:\n\n" +
            "1. Ve a 'Ver Inquilinos'\n" +
            "2. Busca el inquilino deseado\n" +
            "3. Usa los botones 'Ver' o 'Editar'"
        )
    
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