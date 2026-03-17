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
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors, bind_combobox_dropdown_on_click
from manager.app.presenters.tenant_presenter import TenantPresenter
from manager.app.logger import logger

class TenantsView(tk.Frame):
    """Vista principal del módulo de inquilinos con diseño simplificado"""
    
    def __init__(self, parent, on_navigate: Callable = None, on_data_change: Callable = None, on_register_payment: Callable = None, on_new_tenant: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        # Fondo igual al del área de contenido para que no se vea el recuadro blanco
        self.configure(bg=parent.cget("bg"))
        
        self.on_navigate = on_navigate
        self.on_data_change = on_data_change
        self.on_register_payment_callback = on_register_payment
        self.on_new_tenant = on_new_tenant
        self.presenter = TenantPresenter(
            on_navigate=on_navigate,
            on_data_change=on_data_change,
            on_register_payment=on_register_payment,
        )
        self.current_view = "list"
        self.selected_tenant = None

        # Almacenar referencia del scrollable_frame para refrescar lista
        self.scrollable_frame = None

        # Abrir directamente la vista de lista/detalles (sin menú de 3 cards)
        self._show_tenants_list()
    
    def refresh_list(self):
        """Método público para refrescar la lista de inquilinos en tiempo real"""
        try:
            if self.current_view == "list":
                self._load_and_display_tenants()
                logger.debug("Lista de inquilinos refrescada en tiempo real")
        except Exception as e:
            logger.warning("Error al refrescar lista: %s", e)
    
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
        # Frame para botones de navegación
        buttons_frame = tk.Frame(header_frame, bg=bg_view)
        buttons_frame.pack(side="right", padx=10)
        
        # Crear botones con el mismo estilo que otras vistas
        self._create_navigation_buttons_list_view(buttons_frame, self._back_to_dashboard)
        # =================== CONTAINER PRINCIPAL ===================
        main_container = tk.Frame(self, bg=bg_view)
        main_container.pack(fill="both", expand=True, padx=20, pady=(6, 2))
        # =================== COLUMNA IZQUIERDA: cards arriba, búsqueda debajo ===================
        left_column = tk.Frame(main_container, bg=bg_view)
        left_column.pack(side="left", fill="y", padx=(0, 15))
        self._create_action_cards(left_column)
        search_panel = self._create_search_panel(left_column)
        search_panel.pack(fill="both", expand=True, pady=(4, 0))
        # =================== PANEL LISTA (70%) ===================
        list_panel = self._create_list_panel(main_container)
        list_panel.pack(side="right", fill="both", expand=True)
        # =================== CARGAR DATOS ===================
        self._load_and_display_tenants()
        # Enfocar el cuadro de búsqueda al abrir la vista para escribir de inmediato
        self.after(150, self._focus_search_entry)
    
    def _create_search_panel(self, parent):
        """Crea el panel de búsqueda avanzada (compacto, altura según contenido)."""
        panel = tk.Frame(parent, bg="#e3f2fd", relief="solid", bd=2, width=380)
        panel.pack_propagate(True)
        panel.grid_propagate(False)
        # Header más bajo
        header = tk.Frame(panel, bg="#1976d2", height=36)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = tk.Label(
            header,
            text="🔍 Búsqueda Avanzada",
            font=("Segoe UI", 11, "bold"),
            bg="#1976d2",
            fg="white"
        )
        title.pack(expand=True)
        # Contenido: padding inferior justo para que los botones no se corten
        content = tk.Frame(panel, bg="#e3f2fd")
        content.pack(fill="x", padx=6, pady=(4, 6))
        
        # === BÚSQUEDA POR TEXTO: título y descripción en la misma línea ===
        search_title_row = tk.Frame(content, bg="#e3f2fd")
        search_title_row.pack(anchor="w", pady=(0, 2))
        tk.Label(search_title_row, text="Búsqueda general:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(side="left")
        tk.Label(search_title_row, text=" (Nombre, Cédula, Apartamento, Email, Teléfono)", font=("Segoe UI", 8), bg="#e3f2fd", fg="#666666").pack(side="left")
        self.search_entry = tk.Entry(content, font=("Segoe UI", 10), relief="solid", bd=1)
        self.search_entry.pack(fill="x", pady=(0, 4))
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        
        # === FILTRO POR APARTAMENTO ===
        tk.Label(content, text="Filtro por apartamento:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0, 2))
        self.apartment_var = tk.StringVar(value="Todos")
        apartment_combo = ttk.Combobox(content, textvariable=self.apartment_var, font=("Segoe UI", 9))
        apartment_options = self.presenter.get_apartment_options()
        apartment_combo['values'] = apartment_options
        apartment_combo.pack(fill="x", pady=(0, 4))
        apartment_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        bind_combobox_dropdown_on_click(apartment_combo)
        
        # === FILTRO POR ESTADO ===
        tk.Label(content, text="Estado:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0, 2))
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(content, textvariable=self.status_var, font=("Segoe UI", 9))
        status_combo['values'] = ("Todos", "Al Día", "Pendiente Registro", "En Mora", "Inactivo")
        status_combo.pack(fill="x", pady=(0, 4))
        status_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        bind_combobox_dropdown_on_click(status_combo)
        
        # === RANGO DE FECHAS ===
        tk.Label(content, text="Fecha de ingreso:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(2, 1))
        date_frame = tk.Frame(content, bg="#e3f2fd")
        date_frame.pack(fill="x", pady=(0, 2))
        tk.Label(date_frame, text="Desde:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        wrap_from = tk.Frame(date_frame, bg="#e3f2fd", width=110, height=26)
        wrap_from.pack(side="left", padx=(2, 6))
        wrap_from.pack_propagate(False)
        self.date_from = DatePickerWidget(wrap_from)
        self.date_from.pack(fill="both", expand=True)
        tk.Label(date_frame, text="Hasta:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left", padx=(2, 0))
        wrap_to = tk.Frame(date_frame, bg="#e3f2fd", width=110, height=26)
        wrap_to.pack(side="left", padx=2)
        wrap_to.pack_propagate(False)
        self.date_to = DatePickerWidget(wrap_to)
        self.date_to.pack(fill="both", expand=True)
        search_bg = "#e3f2fd"
        for dp in (self.date_from, self.date_to):
            dp.configure(bg=search_bg)
            dp.date_entry.configure(bg=search_bg)
            dp.calendar_btn.configure(bg=search_bg)
        
        # === RANGO DE ARRIENDO ===
        tk.Label(content, text="Rango de arriendo:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(2, 1))
        rent_frame = tk.Frame(content, bg="#e3f2fd")
        rent_frame.pack(fill="x", pady=(0, 2))
        tk.Label(rent_frame, text="Min:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.rent_min = tk.Entry(rent_frame, width=8, font=("Segoe UI", 8))
        self.rent_min.pack(side="left", padx=(2, 6))
        tk.Label(rent_frame, text="Max:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.rent_max = tk.Entry(rent_frame, width=8, font=("Segoe UI", 8))
        self.rent_max.pack(side="left", padx=2)
        
        # === INDICADOR DE RESULTADOS ===
        self.results_indicator = tk.Label(
            content,
            text="📊 Resultados: mostrando todos",
            font=("Segoe UI", 8),
            bg="#e3f2fd",
            fg="#1e40af"
        )
        self.results_indicator.pack(anchor="w", pady=(2, 1))
        
        # === BOTONES (más pequeños) ===
        btn_frame = tk.Frame(content, bg="#e3f2fd")
        btn_frame.pack(fill="x", pady=(1, 2))
        btn_search = tk.Button(
            btn_frame,
            text="🔍 Aplicar",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._apply_filters
        )
        btn_search.pack(side="left", padx=(0, 6))
        btn_clear = tk.Button(
            btn_frame,
            text="🧹 Limpiar",
            font=("Segoe UI", 9),
            bg="#ff9800",
            fg="white",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._clear_filters
        )
        btn_clear.pack(side="left")
        
        return panel

    def _create_action_cards(self, parent):
        """Dos cards encima del panel de búsqueda (Nuevo inquilino y Reportes de inquilinos)."""
        bg_view = parent.cget("bg")
        colors = get_module_colors("inquilinos")
        card_bg = colors.get("primary", "#2563eb")
        card_hover = colors.get("hover", "#1d4ed8")
        cards_frame = tk.Frame(parent, bg=bg_view)
        cards_frame.pack(fill="x", pady=(0, 4))
        # Borde negro: contenedor con fondo negro y relleno para que se vea el borde
        border_width = 2
        # Card Nuevo inquilino (expandido para cubrir espacio)
        wrap_new = tk.Frame(cards_frame, bg="black")
        wrap_new.pack(fill="both", expand=True, pady=(0, 8))
        btn_new = tk.Button(
            wrap_new,
            text="➕ Nuevo inquilino",
            font=("Segoe UI", 11, "bold"),
            bg=card_bg,
            fg="white",
            relief="flat",
            padx=12,
            pady=12,
            cursor="hand2",
            command=self._on_new_tenant_card,
        )
        btn_new.pack(fill="both", expand=True, padx=border_width, pady=border_width)
        btn_new.bind("<Enter>", lambda e: btn_new.config(bg=card_hover))
        btn_new.bind("<Leave>", lambda e: btn_new.config(bg=card_bg))
        # Card Reportes (expandido para cubrir espacio)
        wrap_reports = tk.Frame(cards_frame, bg="black")
        wrap_reports.pack(fill="both", expand=True)
        btn_reports = tk.Button(
            wrap_reports,
            text="📊 Reportes",
            font=("Segoe UI", 11, "bold"),
            bg="#6b7280",
            fg="white",
            relief="flat",
            padx=12,
            pady=12,
            cursor="hand2",
            command=self._on_reports_card,
        )
        btn_reports.pack(fill="both", expand=True, padx=border_width, pady=border_width)
        btn_reports.bind("<Enter>", lambda e: btn_reports.config(bg="#4b5563"))
        btn_reports.bind("<Leave>", lambda e: btn_reports.config(bg="#6b7280"))

    def _on_new_tenant_card(self):
        if self.on_new_tenant:
            self.on_new_tenant()
        elif self.on_navigate:
            self.on_navigate("dashboard")

    def _on_reports_card(self):
        """Abre la vista de reportes de gestión de inquilinos (no reportes generales)."""
        self._show_reports()

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
        """Carga y muestra todos los inquilinos (excluyendo inactivos por defecto)."""
        try:
            self.all_tenants = self.presenter.load_tenants()
            self._apply_filters()
        except Exception as e:
            logger.warning("Error al cargar inquilinos: %s", e)
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
            elif estado in ('pendiente_registro', 'pendiente_pago'):
                pending_tenants.append(tenant)
            else:
                active_tenants.append(tenant)
        
        # Mostrar grupos: primero en mora, luego pendiente de registro, después al día, por último inactivos
        current_row = 0

        if overdue_tenants:
            current_row = self._display_group("⚠️ EN MORA", overdue_tenants, "#ff9800", current_row)

        if pending_tenants:
            current_row = self._display_group("⏰ PENDIENTE DE PAGO", pending_tenants, "#ffc107", current_row)

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
        """Días en mora integral (desde primer período impago). Usa lógica del servicio."""
        try:
            tenant_id = tenant.get("id")
            if not tenant_id:
                return 0
            return tenant_service.get_dias_mora(tenant_id)
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
            'pendiente_pago': 'Pendiente de pago',
            'moroso': 'En mora',
            'inactivo': 'Inactivo'
        }.get(estado_pago, 'Al día')
        if estado_pago == 'moroso':
            info = tenant_service.get_arrears_info(tenant.get("id")) or {}
            meses_mora = info.get("meses_mora", 0)
            dias_del_periodo = info.get("dias_del_periodo_actual", 0)
            if meses_mora > 0 or dias_del_periodo > 0:
                # Si solo debe el período actual (1 mes), mostrar solo los días para no confundir
                if meses_mora == 1:
                    estado_texto = f"En mora ({dias_del_periodo} día{'s' if dias_del_periodo != 1 else ''})"
                else:
                    # Meses completos en mora (el período actual solo cuenta como días)
                    meses_completos = meses_mora - 1
                    partes = []
                    if meses_completos > 0:
                        partes.append(f"{meses_completos} mes{'es' if meses_completos != 1 else ''}")
                    if dias_del_periodo > 0:
                        partes.append(f"{dias_del_periodo} día{'s' if dias_del_periodo != 1 else ''}")
                    estado_texto = "En mora (" + " y ".join(partes) + ")"
            else:
                estado_texto = "En mora"
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
            on_back=self._back_to_list,
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
        """Vuelve al dashboard principal de la aplicación"""
        self.current_view = "list"
        if self.on_navigate:
            self.on_navigate("dashboard")
    
    def _back_to_list(self):
        """Vuelve a la lista de inquilinos"""
        self._show_tenants_list()
    
    def _on_back_clicked(self):
        """Maneja el clic en volver al menú principal"""
        if self.on_navigate:
            self.on_navigate("dashboard")
    
    def _create_navigation_buttons_list_view(self, parent, on_back_command):
        """Crea el botón Dashboard (sin Volver) con estilo moderno y colores azules del módulo de inquilinos"""
        # Colores azules para módulo de inquilinos
        colors = get_module_colors("inquilinos")
        blue_primary = colors["primary"]
        blue_hover = colors["hover"]
        
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

    def _get_filter_state(self) -> dict:
        """Devuelve el estado actual de los filtros para el presenter."""
        if not hasattr(self, "search_entry") or not self.search_entry.winfo_exists():
            return {}
        return {
            "search_text": self.search_entry.get().strip(),
            "apartment": self.apartment_var.get() if hasattr(self, "apartment_var") else "Todos",
            "status": self.status_var.get() if hasattr(self, "status_var") else "Todos",
            "date_from": self.date_from.get().strip() if hasattr(self, "date_from") and hasattr(self.date_from, "get") else "",
            "date_to": self.date_to.get().strip() if hasattr(self, "date_to") and hasattr(self.date_to, "get") else "",
            "rent_min": self.rent_min.get().strip() if hasattr(self, "rent_min") else "",
            "rent_max": self.rent_max.get().strip() if hasattr(self, "rent_max") else "",
        }

    def _on_search_change(self, event=None):
        """Búsqueda en tiempo real"""
        self._apply_filters()

    def _on_filter_change(self, event=None):
        """Aplicar filtros cuando cambian los combos"""
        self._apply_filters()

    def _apply_filters(self):
        """Aplica todos los filtros activos usando el presenter."""
        if not hasattr(self, "all_tenants"):
            return
        filter_state = self._get_filter_state()
        filtered = self.presenter.get_filtered_tenants(self.all_tenants, filter_state)
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
                    logger.warning("Error al actualizar el estado del apartamento: %s", e)
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