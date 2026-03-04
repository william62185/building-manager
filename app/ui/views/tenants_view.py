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
from manager.app.ui.views.tenant_form_view import TenantFormView, DatePickerWidget
from manager.app.ui.views.tenant_details_view import TenantDetailsView
from manager.app.ui.views.deactivate_tenant_view import DeactivateTenantView
import csv
import os
import subprocess
import platform
from datetime import datetime, timedelta
from manager.app.services.apartment_service import apartment_service
from manager.app.services.payment_service import payment_service
from manager.app.services.building_service import building_service
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors

class TenantsView(tk.Frame):
    """Vista principal del módulo de inquilinos con diseño simplificado"""
    
    def __init__(self, parent, on_navigate: Callable = None, on_data_change: Callable = None, on_register_payment: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        # Fondo igual al del área de contenido para que no se vea el recuadro blanco
        self.configure(bg=parent.cget("bg"))
        
        self.on_navigate = on_navigate
        self.on_data_change = on_data_change
        self.on_register_payment_callback = on_register_payment
        self.current_view = "dashboard"
        self.selected_tenant = None
        
        # Almacenar referencia del scrollable_frame para refrescar lista
        self.scrollable_frame = None
        
        # Crear layout principal
        self._create_layout()
    
    def refresh_list(self):
        """Método público para refrescar la lista de inquilinos en tiempo real"""
        try:
            # Si estamos en la vista de lista, recargar y redisplay
            if self.current_view == "list":
                # Recargar datos desde el archivo
                tenant_service._load_data()
                # Recalcular estados basándose en pagos recientes
                tenant_service.recalculate_all_payment_statuses()
                # Recargar datos después del recálculo
                tenant_service._load_data()
                # Volver a mostrar con datos actualizados
                self._load_and_display_tenants()
                print("✅ Lista de inquilinos refrescada en tiempo real")
        except Exception as e:
            print(f"Error al refrescar lista: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _create_layout(self):
        """Crea el layout principal con 4 cards centrales"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Fondo de la vista (transparente respecto al área de contenido)
        bg_view = self.cget("bg")
            
        # Título principal
        title_frame = tk.Frame(self, bg=bg_view)
        title_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(title_frame, bg=bg_view)
        buttons_frame.pack(side="right")
        
        # Colores azules para módulo de inquilinos
        colors = get_module_colors("inquilinos")
        blue_primary = colors["primary"]
        blue_hover = colors["hover"]
        
        # Botón "Dashboard" con esquinas redondeadas
        def go_to_dashboard():
            if self.on_navigate:
                self.on_navigate("dashboard")
        
        btn_dashboard = create_rounded_button(
            buttons_frame,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=blue_primary,
            fg_color="white",
            hover_bg=blue_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")
        
        # Pregunta principal
        theme = theme_manager.themes[theme_manager.current_theme]
        question_label = tk.Label(
            self,
            text="¿Qué deseas hacer?",
            font=("Segoe UI", 14),
            fg=theme["text_primary"],
            bg=bg_view
        )
        question_label.pack(pady=(0, Spacing.XL))
        
        # Contenedor principal centrado (fondo igual al de la vista para que se vea transparente)
        main_container = tk.Frame(self, bg=bg_view)
        main_container.pack(pady=Spacing.LG)
        
        # Grid de cards 2x2 con espaciado optimizado
        self._create_cards_grid(main_container)
    
    def _create_cards_grid(self, parent):
        """Crea el grid de 3 cards principales en una sola fila"""
        bg_view = parent.cget("bg")
        # Centrar todo el contenido (fondo transparente)
        grid_container = tk.Frame(parent, bg=bg_view)
        grid_container.pack(anchor="center")
        
        # Fila única con las tres tarjetas
        row = tk.Frame(grid_container, bg=bg_view)
        row.pack()
        
        # Card 1: Agregar Inquilino
        self._create_action_card(
            row, 
            "➕", 
            "Agregar Inquilino",
            "Registrar un nuevo inquilino en el sistema",
            "#1e40af",  # primary blue
            lambda: self._show_tenant_form()
        ).pack(side="left", padx=Spacing.LG)
        
        # Card 2: Ver Inquilinos  
        self._create_action_card(
            row,
            "👥",
            "Ver/Editar Inquilinos", 
            "Consultar lista completa de inquilinos",
            "#1e40af",  # mismo color que Agregar Inquilino para consistencia
            lambda: self._show_tenants_list()
        ).pack(side="left", padx=Spacing.LG)
        
        # Card 3: Reportes
        self._create_action_card(
            row,
            "📊",
            "Reportes", 
            "Generar reportes y estadísticas",
            "#1e40af",  # mismo color que Agregar Inquilino para consistencia
            lambda: self._show_reports()
        ).pack(side="left", padx=Spacing.LG)
    
    def _create_action_card(self, parent, icon, title, description, color, command):
        """Crea una card de acción con hover effects estilo módulo pagos"""
        # Color azul más intenso para el fondo base de las tarjetas (similar al hover anterior)
        light_blue_bg = "#dbeafe"  # blue-100 - azul claro más intenso para mejor contraste con iconos azules
        
        card_frame = tk.Frame(
            parent,
            bg=light_blue_bg,
            relief="raised",
            bd=2,
            width=260,
            height=220  # Igualar altura a cards de pagos
        )
        card_frame.pack_propagate(False)
        
        # Contenedor principal con padding uniforme para centrar verticalmente
        content_frame = tk.Frame(card_frame, bg=light_blue_bg)
        content_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Frame espaciador superior para centrar el contenido
        top_spacer = tk.Frame(content_frame, bg=light_blue_bg, height=1)
        top_spacer.pack(fill="x", expand=True)
        
        # Contenedor del contenido (icono, título, descripción)
        content_container = tk.Frame(content_frame, bg=light_blue_bg)
        content_container.pack()
        
        icon_label = tk.Label(
            content_container,
            text=icon,
            font=("Segoe UI", 28),
            bg=light_blue_bg,
            fg=color
        )
        icon_label.pack(pady=(0, Spacing.MD))
        
        title_label = tk.Label(
            content_container,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=light_blue_bg,
            fg="#000000"
        )
        title_label.pack()
        
        # Textos descriptivos eliminados según solicitud del usuario
        
        # Frame espaciador inferior para centrar el contenido
        bottom_spacer = tk.Frame(content_frame, bg=light_blue_bg, height=1)
        bottom_spacer.pack(fill="x", expand=True)
        
        def on_enter(event):
            hover_color = "#bfdbfe"  # blue-200 - azul más intenso para hover
            card_frame.configure(bg=hover_color)
            content_frame.configure(bg=hover_color)
            top_spacer.configure(bg=hover_color)
            content_container.configure(bg=hover_color)
            bottom_spacer.configure(bg=hover_color)
            icon_label.configure(bg=hover_color)
            title_label.configure(bg=hover_color)
        
        def on_leave(event):
            card_frame.configure(bg=light_blue_bg)
            content_frame.configure(bg=light_blue_bg)
            top_spacer.configure(bg=light_blue_bg)
            content_container.configure(bg=light_blue_bg)
            bottom_spacer.configure(bg=light_blue_bg)
            icon_label.configure(bg=light_blue_bg)
            title_label.configure(bg=light_blue_bg)
        
        def on_card_click(event):
            command()
        
        # Hacer TODO el card clickeable - bind a todos los elementos
        # Esto asegura que cualquier parte del card responda al clic
        all_widgets = [card_frame, content_frame, top_spacer, content_container, bottom_spacer, icon_label, title_label]
        for widget in all_widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_card_click)
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
            on_save_success=self.on_data_change,
            on_navigate_to_dashboard=lambda: self.on_navigate("dashboard") if self.on_navigate else None
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_tenants_list(self):
        """VERSIÓN COMPLETA - Sistema avanzado de gestión de inquilinos"""
        self.current_view = "list"
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        # =================== HEADER ===================
        bg_view = self.cget("bg")
        header_frame = tk.Frame(self, bg=bg_view)
        header_frame.pack(fill="x", pady=(0, 15))
        title_label = tk.Label(
            header_frame,
            text="👁️ Ver detalles inquilinos",
            font=("Segoe UI", 18, "bold"),
            bg=bg_view,
            fg="#000000"
        )
        title_label.pack(side="left", padx=10)
        
        # Frame para botones de navegación
        buttons_frame = tk.Frame(header_frame, bg=bg_view)
        buttons_frame.pack(side="right", padx=10)
        
        # Crear botones con el mismo estilo que otras vistas
        self._create_navigation_buttons_list_view(buttons_frame, self._back_to_dashboard)
        # =================== CONTAINER PRINCIPAL ===================
        main_container = tk.Frame(self, bg=bg_view)
        main_container.pack(fill="both", expand=True, padx=20, pady=(6, 2))
        # =================== PANEL BÚSQUEDA (30%) ===================
        search_panel = self._create_search_panel(main_container)
        search_panel.pack(side="left", fill="y", padx=(0, 15))
        # =================== PANEL LISTA (70%) ===================
        list_panel = self._create_list_panel(main_container)
        list_panel.pack(side="right", fill="both", expand=True)
        # =================== CARGAR DATOS ===================
        self._load_and_display_tenants()
        # Enfocar el cuadro de búsqueda al abrir la vista para escribir de inmediato
        self.after(150, self._focus_search_entry)
    
    def _create_search_panel(self, parent):
        """Crea el panel de búsqueda avanzada"""
        # Panel más alto para usar el espacio inferior (reducido padding global)
        panel = tk.Frame(parent, bg="#e3f2fd", relief="solid", bd=2, width=380, height=640)
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
        # Contenido del panel - REDUCIR PADDING para dar más espacio a los botones
        content = tk.Frame(panel, bg="#e3f2fd")
        content.pack(fill="both", expand=True, padx=8, pady=8)
        
        # === BÚSQUEDA POR TEXTO ===
        tk.Label(content, text="Búsqueda general:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,2))
        tk.Label(content, text="(Nombre, Cédula, Apartamento, Email, Teléfono)", font=("Segoe UI", 8), bg="#e3f2fd", fg="#666666").pack(anchor="w", pady=(0,5))
        self.search_entry = tk.Entry(content, font=("Segoe UI", 10), relief="solid", bd=1)
        self.search_entry.pack(fill="x", pady=(0,8))
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        
        # === FILTRO POR APARTAMENTO ===
        tk.Label(content, text="Filtro por apartamento:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,5))
        self.apartment_var = tk.StringVar(value="Todos")
        apartment_combo = ttk.Combobox(content, textvariable=self.apartment_var, font=("Segoe UI", 10))
        
        # Obtener apartamentos reales de la base de datos
        apartment_options = ["Todos"]
        try:
            from manager.app.services.apartment_service import apartment_service
            apartments = apartment_service.get_all_apartments()
            for apt in apartments:
                apt_number = apt.get('number', '')
                apt_type = apt.get('unit_type', 'Apartamento Estándar')
                if apt_type == "Apartamento Estándar":
                    apartment_options.append(apt_number)
                else:
                    apartment_options.append(f"{apt_type} {apt_number}")
        except Exception as e:
            print(f"Error al cargar apartamentos: {e}")
            # Fallback a valores básicos si hay error
            apartment_options.extend(["101", "102", "201", "202", "301", "302"])
        
        apartment_combo['values'] = apartment_options
        apartment_combo.pack(fill="x", pady=(0,8))
        apartment_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # === FILTRO POR ESTADO ===
        tk.Label(content, text="Estado:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,5))
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(content, textvariable=self.status_var, font=("Segoe UI", 10))
        status_combo['values'] = ("Todos", "Al Día", "Pendiente Registro", "En Mora", "Inactivo")
        status_combo.pack(fill="x", pady=(0,8))
        status_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # === RANGO DE FECHAS (CON SELECTOR DE CALENDARIO) ===
        tk.Label(content, text="Fecha de ingreso:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(3,2))
        
        date_frame = tk.Frame(content, bg="#e3f2fd")
        date_frame.pack(fill="x", pady=(0,3))
        
        # Una sola línea: campos de fecha con ancho y altura fijos (botón calendario visible)
        tk.Label(date_frame, text="Desde:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        wrap_from = tk.Frame(date_frame, bg="#e3f2fd", width=118, height=30)
        wrap_from.pack(side="left", padx=(3, 8))
        wrap_from.pack_propagate(False)
        self.date_from = DatePickerWidget(wrap_from)
        self.date_from.pack(fill="both", expand=True)
        
        tk.Label(date_frame, text="Hasta:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left", padx=(4, 0))
        wrap_to = tk.Frame(date_frame, bg="#e3f2fd", width=118, height=30)
        wrap_to.pack(side="left", padx=3)
        wrap_to.pack_propagate(False)
        self.date_to = DatePickerWidget(wrap_to)
        self.date_to.pack(fill="both", expand=True)
        
        # === RANGO DE ARRIENDO (COMPACTO) ===
        tk.Label(content, text="Rango de arriendo:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(3,2))
        
        rent_frame = tk.Frame(content, bg="#e3f2fd")
        rent_frame.pack(fill="x", pady=(0,3))
        
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
            fg="#1e40af"  # Azul oscuro para mantener tonalidad azul
        )
        self.results_indicator.pack(anchor="w", pady=(5,5))
        
        # === BOTONES ===
        btn_frame = tk.Frame(content, bg="#e3f2fd")
        btn_frame.pack(fill="x", pady=(5,0))
        
        btn_search = tk.Button(
            btn_frame,
            text="🔍 Aplicar",
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",  # Azul para mantener tonalidad azul del módulo
            fg="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._apply_filters
        )
        btn_search.pack(side="left", padx=(0,8))
        
        btn_clear = tk.Button(
            btn_frame,
            text="🧹 Limpiar",
            font=("Segoe UI", 10),
            bg="#ff9800",
            fg="white",
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
            command=self._clear_filters
        )
        btn_clear.pack(side="left")
        
        return panel
    
    def _create_list_panel(self, parent):
        """Crea el panel de lista de inquilinos con tonalidad azul"""
        # Aplicando regla 60-30-10: 60% azul claro, 30% blanco, 10% azul oscuro
        panel_bg = "#e0f2fe"  # sky-50 - azul muy claro (60% fondo predominante)
        header_bg = "#1e40af"  # blue-800 - azul oscuro para header (10% acento)
        header_text_light = "#bfdbfe"  # sky-200 - azul claro para texto secundario
        
        panel = tk.Frame(parent, bg=panel_bg, relief="solid", bd=2)
        header = tk.Frame(panel, bg=header_bg, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        header_content = tk.Frame(header, bg=header_bg)
        header_content.pack(expand=True)
        self.list_title = tk.Label(
            header_content,
            text="📋 Lista de Inquilinos",
            font=("Segoe UI", 12, "bold"),
            bg=header_bg,
            fg="white"
        )
        self.list_title.pack(side="left", padx=15)
        self.counter_label = tk.Label(
            header_content,
            text="(0 inquilinos)",
            font=("Segoe UI", 10),
            bg=header_bg,
            fg=header_text_light  # Azul claro para texto secundario
        )
        self.counter_label.pack(side="left", padx=5)
        self.scroll_frame = tk.Frame(panel, bg=panel_bg)
        self.scroll_frame.pack(fill="both", expand=True, padx=8, pady=6)
        self.canvas = tk.Canvas(self.scroll_frame, bg=panel_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=panel_bg)
        # Guardar referencia del scrollable_frame como atributo de instancia para acceso externo
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
        """Carga y muestra todos los inquilinos (excluyendo inactivos por defecto)"""
        try:
            # Recargar datos desde el archivo para asegurar datos actualizados
            tenant_service._load_data()
            
            # Recalcular estados de pago automáticamente antes de cargar
            # Esto asegura que los estados se actualicen basándose en los pagos más recientes
            tenant_service.recalculate_all_payment_statuses()
            
            # Recargar datos nuevamente después del recálculo para obtener estados actualizados
            tenant_service._load_data()
            
            # Cargar inquilinos actualizados (después de recargar y recalcular)
            self.all_tenants = tenant_service.get_all_tenants()
            
            # Aplicar filtros (esto excluirá inactivos por defecto si el estado es "Todos")
            self._apply_filters()
        except Exception as e:
            print(f"Error al cargar inquilinos: {str(e)}")
            self.all_tenants = []
            self._display_tenants([])
    
    def _show_empty_state(self):
        """Muestra mensaje cuando no hay inquilinos que coincidan con los filtros"""
        self.counter_label.config(text="(0 inquilinos)")
        msg = tk.Label(
            self.scrollable_frame,
            text="No hay inquilinos que coincidan con los filtros.\nPrueba ajustar o limpiar los criterios de búsqueda.",
            font=("Segoe UI", 11),
            bg="#e0f2fe",  # Azul claro para mantener tonalidad azul
            fg="#666666",
            justify="center"
        )
        msg.pack(pady=40, padx=20)
        if hasattr(self, 'results_indicator'):
            all_tenants = getattr(self, 'all_tenants', [])
            total_active = len([t for t in all_tenants if t.get('estado_pago') != 'inactivo'])
            self.results_indicator.config(
                text=f"🔍 Resultados: 0 de {total_active} inquilinos",
                fg="#1976d2"
            )

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
        pending_tenants = []
        overdue_tenants = []
        inactive_tenants = []
        
        for tenant in tenants:
            estado = tenant.get('estado_pago', 'al_dia')
            if estado == 'inactivo':
                inactive_tenants.append(tenant)
            elif estado == 'moroso':
                overdue_tenants.append(tenant)
            elif estado == 'pendiente_registro':
                pending_tenants.append(tenant)
            else:
                active_tenants.append(tenant)
        
        # Mostrar grupos: primero en mora, luego pendiente de registro, después al día, por último inactivos
        current_row = 0

        if overdue_tenants:
            current_row = self._display_group("⚠️ EN MORA", overdue_tenants, "#ff9800", current_row)

        if pending_tenants:
            current_row = self._display_group("⏰ PENDIENTE REGISTRO", pending_tenants, "#ffc107", current_row)

        if active_tenants:
            current_row = self._display_group("✅ AL DÍA", active_tenants, "#2563eb", current_row)

        if inactive_tenants:
            current_row = self._display_group("❌ INACTIVOS", inactive_tenants, "#f44336", current_row)
        
        # Actualizar contador
        total = len(tenants)
        self.counter_label.config(text=f"({total} inquilino{'s' if total != 1 else ''})")
        
        # Actualizar indicador de resultados en el panel de búsqueda (solo cuenta inquilinos activos)
        if hasattr(self, 'results_indicator'):
            all_tenants = getattr(self, 'all_tenants', [])
            total_active = len([t for t in all_tenants if t.get('estado_pago') != 'inactivo'])
            if total == total_active:
                self.results_indicator.config(
                    text="📊 Resultados: mostrando todos",
                    fg="#1e40af"  # Azul oscuro para mantener tonalidad azul
                )
            else:
                self.results_indicator.config(
                    text=f"🔍 Resultados: {total} de {total_active} inquilinos",
                    fg="#1976d2"
                )
        
        # Forzar actualización del scroll
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Forzar actualización completa de Tkinter
        self.update_idletasks()
        self.update()
    
    def _display_group(self, title, tenants, color, start_row):
        """Muestra un grupo de inquilinos"""
        # Separador y título del grupo
        separator = tk.Frame(self.scrollable_frame, bg=color, height=2)
        separator.pack(fill="x", pady=(4, 0))
        
        group_title = tk.Label(
            self.scrollable_frame,
            text=f"{title} ({len(tenants)})",
            font=("Segoe UI", 11, "bold"),
            bg="#e0f2fe",
            fg=color
        )
        group_title.pack(anchor="w", pady=(2, 3))
        
        # Inquilinos del grupo
        for i, tenant in enumerate(tenants):
            self._create_tenant_row(tenant, color, i % 2 == 0)
        
        return start_row + len(tenants)
    
    def _get_dias_mora(self, tenant):
        """Calcula los días en mora para un inquilino moroso. Retorna 0 si no aplica o hay error."""
        try:
            tenant_id = tenant.get("id")
            if not tenant_id:
                return 0
            hoy = datetime.now()
            payments = payment_service.get_payments_by_tenant(tenant_id)
            if payments:
                payments.sort(key=lambda x: datetime.strptime(x.get("fecha_pago", "01/01/1900"), "%d/%m/%Y"), reverse=True)
                ultimo = payments[0]
                fecha_ultimo_str = ultimo.get("fecha_pago", "")
                if fecha_ultimo_str:
                    fecha_ultimo = datetime.strptime(fecha_ultimo_str, "%d/%m/%Y")
                    fecha_vencimiento = fecha_ultimo + timedelta(days=30)
                    if hoy > fecha_vencimiento:
                        return (hoy - fecha_vencimiento).days
            else:
                fecha_ingreso = tenant.get("fecha_ingreso", "")
                if fecha_ingreso:
                    try:
                        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%d/%m/%Y")
                        dia_pago = fecha_ingreso_dt.day
                        try:
                            venc_este_mes = hoy.replace(day=min(dia_pago, 28))
                            if venc_este_mes <= hoy:
                                return max(0, (hoy - venc_este_mes).days)
                            mes_ant = (hoy.replace(day=1) - timedelta(days=1))
                            venc_ant = mes_ant.replace(day=min(dia_pago, 28))
                            return max(0, (hoy - venc_ant).days)
                        except ValueError:
                            venc_este_mes = hoy.replace(day=1)
                            return max(0, (hoy - venc_este_mes).days)
                    except Exception:
                        pass
            return 0
        except Exception:
            return 0

    def _create_tenant_row(self, tenant, status_color, is_even):
        """Crea una fila para un inquilino con información completa y clic"""
        bg_color = "#ffffff" if is_even else "#f8f9fa"
        row_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief="solid", bd=1)
        row_frame.pack(fill="x", pady=0)
        content = tk.Frame(row_frame, bg=bg_color)
        content.pack(fill="x", padx=10, pady=4)
        name = tenant.get('nombre', 'Sin nombre')
        apartment_id = tenant.get('apartamento', None)
        apartment_display = 'N/A'
        if apartment_id is not None:
            try:
                apartment_id_int = int(apartment_id)
            except Exception:
                apartment_id_int = apartment_id
            apt = apartment_service.get_apartment_by_id(apartment_id_int) if hasattr(apartment_service, 'get_apartment_by_id') else None
            if not apt:
                all_apts = apartment_service.get_all_apartments()
                apt = next((a for a in all_apts if a.get('id') == apartment_id_int), None)
            if apt:
                building = None
                if hasattr(building_service, 'get_building_by_id'):
                    building = building_service.get_building_by_id(apt.get('building_id'))
                else:
                    all_buildings = building_service.get_all_buildings()
                    building = next((b for b in all_buildings if b.get('id') == apt.get('building_id')), None)
                building_name = building.get('name') if building else ''
                tipo = apt.get('unit_type', 'Apartamento Estándar')
                numero = apt.get('number', '')
                if building_name:
                    apartment_display = f"{building_name} - {tipo} {numero}" if tipo != 'Apartamento Estándar' else f"{building_name} - {numero}"
                else:
                    apartment_display = f"{tipo} {numero}" if tipo != 'Apartamento Estándar' else str(numero)
        valor_arriendo = tenant.get('valor_arriendo', 0)
        if valor_arriendo is not None and valor_arriendo != "":
            try:
                valor_arriendo_num = float(valor_arriendo)
                valor_arriendo_display = f"${valor_arriendo_num:,.0f}"
            except Exception:
                valor_arriendo_display = str(valor_arriendo)
        else:
            valor_arriendo_display = "No registrado"
        estado_pago = tenant.get('estado_pago', 'al_dia')
        estado_texto = {
            'al_dia': 'Al día',
            'pendiente_registro': 'Pendiente Registro',
            'moroso': 'En mora',
            'inactivo': 'Inactivo'
        }.get(estado_pago, 'Al día')
        if estado_pago == 'moroso':
            dias_mora = self._get_dias_mora(tenant)
            estado_texto = f"En mora ({dias_mora} días)" if dias_mora > 0 else "En mora"
        # Día de pago (para poner en la misma línea que el estado)
        fecha_ingreso = tenant.get('fecha_ingreso', None)
        dia_pago = None
        if fecha_ingreso:
            try:
                dia_pago = int(fecha_ingreso.split('/')[0])
            except Exception:
                dia_pago = None

        main_info = tk.Label(
            content,
            text=f"👤 {name}",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            anchor="w"
        )
        main_info.pack(anchor="w", pady=(0, 0))
        details = tk.Label(
            content,
            text=f"🏠 Apto: {apartment_display} | 💰 Arriendo: {valor_arriendo_display} | 📞 Teléfono: {tenant.get('telefono', 'No registrado')}",
            font=("Segoe UI", 9),
            bg=bg_color,
            anchor="w"
        )
        details.pack(anchor="w", pady=(1, 0))
        # Línea única: Día de pago + Estado (Al día / En mora)
        payment_line = tk.Frame(content, bg=bg_color)
        payment_line.pack(anchor="w", pady=(1, 0))
        dia_pago_label = None
        if dia_pago:
            dia_pago_label = tk.Label(
                payment_line,
                text=f"📅 Día de pago: {dia_pago} de cada mes",
                font=("Segoe UI", 9),
                bg=bg_color,
                fg="#1976d2",
                anchor="w"
            )
            dia_pago_label.pack(side="left")
        estado_label = tk.Label(
            payment_line,
            text=f"  ● {estado_texto}" if dia_pago else f"● {estado_texto}",
            font=("Segoe UI", 9, "bold"),
            fg=status_color,
            bg=bg_color
        )
        estado_label.pack(side="left")
        
        # Frame para botones de acción
        actions_frame = tk.Frame(content, bg=bg_color)
        actions_frame.pack(anchor="w", pady=(2, 0))
        
        # Comprobar si el inquilino tiene pagos: si tiene, Eliminar se deshabilita
        tenant_id = tenant.get("id")
        has_payments = bool(tenant_id and len(payment_service.get_payments_by_tenant(tenant_id)) > 0)
        
        # Botón Desactivar inquilino (abre la vista de desactivar con este inquilino preseleccionado)
        deactivate_btn = tk.Button(
            actions_frame,
            text="🚫 Desactivar inquilino",
            font=("Segoe UI", 8),
            bg="#f59e0b",
            fg="white",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda t=tenant: self._open_desactivar_for_tenant(t)
        )
        deactivate_btn.pack(side="left", padx=(0, 6))
        
        # Botón de eliminar (deshabilitado si tiene al menos un pago registrado)
        delete_btn = tk.Button(
            actions_frame,
            text="🗑️ Eliminar",
            font=("Segoe UI", 8),
            bg="#dc2626",
            fg="white",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2" if not has_payments else "arrow",
            state="normal" if not has_payments else "disabled",
            command=lambda t=tenant: self._confirm_delete_tenant(t)
        )
        delete_btn.pack(side="left")
        if has_payments:
            delete_btn.configure(fg="#9ca3af", bg="#d1d5db")
        
        # Hacer clic en el card para ver detalles - MEJORADO: toda el área es clickeable
        def on_card_click(event, t=tenant):
            # Verificar que el clic no fue en los botones de acción o su frame
            clicked_widget = event.widget
            if clicked_widget in (delete_btn, deactivate_btn, actions_frame):
                return
            try:
                parent = clicked_widget.winfo_parent()
                if parent == str(delete_btn) or parent == str(deactivate_btn) or parent == str(actions_frame):
                    return
            except:
                pass
            self._show_tenant_details(t)
        
        # Bind a TODO el card y TODOS sus hijos para hacer toda el área clickeable
        all_clickable_widgets = [row_frame, content, main_info, details, payment_line, estado_label]
        if dia_pago_label is not None:
            all_clickable_widgets.append(dia_pago_label)
        
        for widget in all_clickable_widgets:
            widget.bind("<Button-1>", on_card_click)
            widget.configure(cursor="hand2")
    
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
            on_register_payment=self.on_register_payment_callback,
            on_navigate_to_dashboard=lambda: self.on_navigate("dashboard") if self.on_navigate else None
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
            on_save_success=self.on_data_change,
            on_navigate_to_dashboard=lambda: self.on_navigate("dashboard") if self.on_navigate else None
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_edit_options(self):
        """(Eliminado: ya no se usa EditDeleteTenantsView)"""
        pass
    
    def _show_reports(self):
        """Muestra la vista completa de reportes específicos de gestión de inquilinos"""
        self.current_view = "reports"
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Importar e instanciar la vista de reportes específica de gestión de inquilinos
        from manager.app.ui.views.tenant_management_reports_view import TenantManagementReportsView
        
        reports_view = TenantManagementReportsView(
            self,
            on_back=self._back_to_dashboard,
            on_navigate=lambda: self.on_navigate("dashboard") if self.on_navigate else None
        )
        reports_view.pack(fill="both", expand=True)
    
    def _open_desactivar_for_tenant(self, tenant):
        """Abre la vista de desactivar inquilino con el inquilino preseleccionado (misma lógica y vista que Administración)."""
        self.current_view = "deactivate"
        for widget in self.winfo_children():
            widget.destroy()
        
        def _on_desactivar_done():
            if self.on_data_change:
                self.on_data_change()
            self._back_to_list()
        
        deactivate_view = DeactivateTenantView(
            self,
            on_back=self._back_to_list,
            on_success=_on_desactivar_done,
            on_navigate=self.on_navigate,
            initial_tenant=tenant
        )
        deactivate_view.pack(fill="both", expand=True)
    
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
    
    def _create_navigation_buttons_list_view(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo moderno y colores azules del módulo de inquilinos"""
        # Colores azules para módulo de inquilinos
        colors = get_module_colors("inquilinos")
        blue_primary = colors["primary"]
        blue_hover = colors["hover"]
        blue_light = colors["light"]
        blue_text = colors["text"]
        
        # Botón "Volver" con esquinas ligeramente redondeadas y borde negro
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=blue_primary,
            hover_bg=blue_light,
            hover_fg=blue_text,
            command=on_back_command,
            padx=16,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard" con esquinas ligeramente redondeadas y borde negro
        def go_to_dashboard():
            if self.on_navigate:
                self.on_navigate("dashboard")
        
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=blue_primary,
            fg_color="white",
            hover_bg=blue_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")

    def _focus_search_entry(self):
        """Coloca el foco en el cuadro de búsqueda general al abrir la vista."""
        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.focus_set()

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
            def matches_apartment_number(tenant):
                from manager.app.services.apartment_service import apartment_service
                apt_id = tenant.get('apartamento', None)
                if apt_id is not None:
                    apt = apartment_service.get_apartment_by_id(apt_id) if hasattr(apartment_service, 'get_apartment_by_id') else None
                    if not apt:
                        all_apts = apartment_service.get_all_apartments()
                        apt = next((a for a in all_apts if a.get('id') == apt_id), None)
                    if apt:
                        num = str(apt.get('number', '')).lower()
                        return search_text in num
                return False
            filtered = [t for t in filtered if 
                       search_text in str(t.get('nombre', '')).lower() or
                       search_text in str(t.get('numero_documento', '')).lower() or
                       matches_apartment_number(t) or
                       search_text in str(t.get('email', '')).lower() or
                       search_text in str(t.get('telefono', '')).lower()]
        # Filtro por apartamento (combo) - Solo aplica si no se buscó apartamento en texto
        apartment = self.apartment_var.get()
        if apartment != "Todos" and not search_text:
            # Buscar inquilinos que coincidan con el apartamento seleccionado
            def matches_apartment_filter(tenant):
                from manager.app.services.apartment_service import apartment_service
                apt_id = tenant.get('apartamento', None)
                if apt_id is not None:
                    apt = apartment_service.get_apartment_by_id(apt_id) if hasattr(apartment_service, 'get_apartment_by_id') else None
                    if not apt:
                        all_apts = apartment_service.get_all_apartments()
                        apt = next((a for a in all_apts if a.get('id') == apt_id), None)
                    if apt:
                        apt_number = apt.get('number', '')
                        apt_type = apt.get('unit_type', 'Apartamento Estándar')
                        if apt_type == "Apartamento Estándar":
                            apt_display = apt_number
                        else:
                            apt_display = f"{apt_type} {apt_number}"
                        return apt_display == apartment
                return False
            filtered = [t for t in filtered if matches_apartment_filter(t)]
        elif apartment != "Todos" and search_text:
            # Si hay búsqueda de texto, aplicar el mismo filtro
            def matches_apartment_filter(tenant):
                from manager.app.services.apartment_service import apartment_service
                apt_id = tenant.get('apartamento', None)
                if apt_id is not None:
                    apt = apartment_service.get_apartment_by_id(apt_id) if hasattr(apartment_service, 'get_apartment_by_id') else None
                    if not apt:
                        all_apts = apartment_service.get_all_apartments()
                        apt = next((a for a in all_apts if a.get('id') == apt_id), None)
                    if apt:
                        apt_number = apt.get('number', '')
                        apt_type = apt.get('unit_type', 'Apartamento Estándar')
                        if apt_type == "Apartamento Estándar":
                            apt_display = apt_number
                        else:
                            apt_display = f"{apt_type} {apt_number}"
                        return apt_display == apartment
                return False
            filtered = [t for t in filtered if matches_apartment_filter(t)]
        # Filtro por estado
        status = self.status_var.get()
        if status != "Todos":
            status_mapping = {
                "Al Día": "al_dia",
                "Pendiente Registro": "pendiente_registro",
                "En Mora": "moroso",
                "Inactivo": "inactivo"
            }
            target_status = status_mapping.get(status, status.lower())
            filtered = [t for t in filtered if t.get('estado_pago') == target_status]
        else:
            # Por defecto, cuando es "Todos", excluir inquilinos inactivos
            filtered = [t for t in filtered if t.get('estado_pago') != 'inactivo']
        # Filtro por rango de fecha de ingreso
        date_from_str = self.date_from.get().strip() if hasattr(self.date_from, 'get') else ''
        date_to_str = self.date_to.get().strip() if hasattr(self.date_to, 'get') else ''
        if date_from_str or date_to_str:
            def parse_date(s):
                try:
                    return datetime.strptime(s.strip(), "%d/%m/%Y").date()
                except (ValueError, AttributeError):
                    return None
            d_from = parse_date(date_from_str) if date_from_str else None
            d_to = parse_date(date_to_str) if date_to_str else None
            def in_date_range(tenant):
                fi = tenant.get('fecha_ingreso') or ''
                if not fi:
                    return False
                d = parse_date(fi)
                if d is None:
                    return False
                if d_from is not None and d < d_from:
                    return False
                if d_to is not None and d > d_to:
                    return False
                return True
            filtered = [t for t in filtered if in_date_range(t)]
        # Filtro por rango de arriendo (Min / Max)
        rent_min_str = self.rent_min.get().strip()
        rent_max_str = self.rent_max.get().strip()
        if rent_min_str or rent_max_str:
            def parse_rent(s):
                """Convierte a número: acepta 400000, 500000.0 (decimal), 400.000 o 1.000.000 (miles)."""
                try:
                    s = str(s).strip().replace(",", "")
                    if not s:
                        return None
                    # Si hay punto: puede ser decimal (500000.0) o miles (1.000.000)
                    if "." in s:
                        parts = s.split(".")
                        # Un solo punto y 1-2 dígitos después = decimal (ej. 500000.0)
                        if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
                            return float(s)
                        # Varios puntos o 3 dígitos después = separador de miles
                        return float(s.replace(".", ""))
                    return float(s)
                except (ValueError, TypeError):
                    return None
            r_min = parse_rent(rent_min_str) if rent_min_str else None
            r_max = parse_rent(rent_max_str) if rent_max_str else None
            def in_rent_range(tenant):
                val = tenant.get('valor_arriendo')
                if val is None or val == "":
                    return False
                rent = parse_rent(val)
                if rent is None:
                    return False
                if r_min is not None and rent < r_min:
                    return False
                if r_max is not None and rent > r_max:
                    return False
                return True
            filtered = [t for t in filtered if in_rent_range(t)]
        self._display_tenants(filtered)

    def _clear_filters(self):
        """Limpia todos los filtros"""
        self.search_entry.delete(0, tk.END)
        self.apartment_var.set("Todos")
        self.status_var.set("Todos")
        self.date_from.set("")
        self.date_to.set("")
        self.rent_min.delete(0, tk.END)
        self.rent_max.delete(0, tk.END)
        if hasattr(self, 'all_tenants'):
            # Aplicar filtros para excluir inactivos por defecto
            self._apply_filters()

    def _confirm_delete_tenant(self, tenant):
        nombre = tenant.get("nombre", "Inquilino")
        if messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas eliminar a {nombre}? Esta acción no se puede deshacer."):
            # Liberar apartamento si corresponde
            apt_id = tenant.get("apartamento")
            if apt_id is not None:
                try:
                    from manager.app.services.apartment_service import apartment_service
                    apartment_service.update_apartment(apt_id, {"status": "Disponible"})
                except Exception as e:
                    print(f"Error al actualizar el estado del apartamento: {e}")
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
        from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
        ensure_dirs()
        ruta = str(EXPORTS_DIR / "inquilinos_exportados.csv")
        try:
            with open(ruta, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([h[0] for h in headers])
                for t in tenants:
                    row = [t.get(h[1], "") for h in headers]
                    writer.writerow(row)
            
            # Mostrar diálogo personalizado con ruta copiable
            self._show_export_success_dialog(ruta)
        except Exception as e:
            messagebox.showerror("Exportar", f"Error al exportar: {str(e)}")

    def _show_export_success_dialog(self, file_path: str):
        """Muestra un diálogo personalizado con la ruta del archivo exportado"""
        dialog = tk.Toplevel(self)
        dialog.title("Exportar")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.update_idletasks()
        width = 550
        height = 200
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Icono y mensaje
        info_frame = tk.Frame(main_frame, bg="white")
        info_frame.pack(fill="x", pady=(0, 15))
        
        # Icono de información
        icon_label = tk.Label(
            info_frame,
            text="ℹ️",
            font=("Segoe UI", 24),
            bg="white",
            fg="#1976d2"
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Texto del mensaje
        text_frame = tk.Frame(info_frame, bg="white")
        text_frame.pack(side="left", fill="x", expand=True)
        
        msg_label = tk.Label(
            text_frame,
            text="Exportación exitosa. Archivo guardado en:",
            font=("Segoe UI", 10),
            bg="white",
            fg="#333",
            anchor="w"
        )
        msg_label.pack(fill="x")
        
        # Campo de entrada con la ruta (seleccionable)
        path_frame = tk.Frame(main_frame, bg="white")
        path_frame.pack(fill="x", pady=(0, 15))
        
        path_entry = tk.Entry(
            path_frame,
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            bg="#ffffff",
            fg="#000000",
            selectbackground="#1976d2",
            selectforeground="white",
            readonlybackground="#ffffff",
            insertbackground="#000000"
        )
        path_entry.pack(side="left", fill="x", expand=True, ipady=5)
        # Insertar texto primero, luego configurar como readonly
        path_entry.config(state="normal")
        path_entry.insert(0, file_path)
        path_entry.config(state="readonly")
        # Seleccionar todo el texto para que sea visible y fácil de copiar
        path_entry.select_range(0, tk.END)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill="x")
        
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(file_path)
            dialog.update()
            copy_btn.config(text="✓ Copiado", bg="#2563eb")  # Azul para mantener tonalidad azul
            dialog.after(1500, lambda: copy_btn.config(text="📋 Copiar", bg="#1976d2"))
        
        def open_folder():
            folder_path = os.path.dirname(file_path)
            try:
                if platform.system() == "Windows":
                    # Usar explorer.exe /select para abrir la carpeta y seleccionar el archivo
                    subprocess.Popen(['explorer.exe', '/select,', os.path.normpath(file_path)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", "-R", file_path])  # -R revela el archivo en Finder
                else:  # Linux
                    # Para Linux, intentar usar el gestor de archivos con selección de archivo
                    try:
                        subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
                    except:
                        subprocess.Popen(["nautilus", "--select", file_path])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta: {str(e)}")
        
        copy_btn = tk.Button(
            buttons_frame,
            text="📋 Copiar",
            font=("Segoe UI", 9, "bold"),
            bg="#1976d2",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=copy_to_clipboard
        )
        copy_btn.pack(side="left", padx=(0, 10))
        
        open_btn = tk.Button(
            buttons_frame,
            text="📂 Abrir carpeta",
            font=("Segoe UI", 9),
            bg="#666",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=open_folder
        )
        open_btn.pack(side="left", padx=(0, 10))
        
        ok_btn = tk.Button(
            buttons_frame,
            text="Aceptar",
            font=("Segoe UI", 9, "bold"),
            bg="#1976d2",
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2",
            command=dialog.destroy
        )
        ok_btn.pack(side="right")
        
        # Permitir copiar con Ctrl+C en el campo de entrada
        path_entry.bind("<Control-c>", lambda e: copy_to_clipboard())
        
        # Enfocar el campo de entrada para facilitar selección
        path_entry.focus_set()
        
        # Hacer el diálogo modal
        dialog.wait_window()
    
    def on_register_payment(self, tenant):
        # Llama a la función de navegación real si está disponible
        if self.on_register_payment_callback:
            self.on_register_payment_callback(tenant)
            return
        from tkinter import messagebox
        messagebox.showinfo("Navegación", "No se pudo navegar al módulo de pagos.")