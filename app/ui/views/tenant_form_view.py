"""
Formulario profesional para gestión de inquilinos
Incluye validaciones, diseño moderno y manejo de estados
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Callable
import re
import calendar
from datetime import datetime, date
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from ..components.modern_widgets import (
    ModernButton, ModernCard, ModernEntry,
    ModernBadge, ModernSeparator, create_rounded_button, get_module_colors
)
from manager.app.services.tenant_service import tenant_service
from manager.app.paths_config import (
    DOCUMENTOS_INQUILINOS_DIR,
    ensure_dirs,
    get_tenant_document_folder_name,
)

class DatePickerWidget(tk.Frame):
    """Widget personalizado para selección de fechas con calendario"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.selected_date = None
        self.calendar_window = None
        
        # Crear el widget principal
        self._create_widget()
    
    def _create_widget(self):
        """Crea el widget de selección de fecha"""
        # Botón para abrir el calendario (empaquetar primero para reservar espacio a la derecha)
        self.calendar_btn = tk.Button(
            self,
            text="📅",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=3,
            cursor="hand2",
            command=self._show_calendar
        )
        self.calendar_btn.pack(side="right", padx=(4, 0))
        
        # Campo de entrada para mostrar la fecha seleccionada (ocupa el espacio restante)
        self.date_entry = tk.Entry(self, **theme_manager.get_style("entry"))
        self.date_entry.pack(side="left", fill="x", expand=True)
    
    def _show_calendar(self):
        """Muestra el calendario en una ventana emergente"""
        if self.calendar_window:
            self.calendar_window.destroy()
        
        # Crear ventana del calendario más compacta
        self.calendar_window = tk.Toplevel(self)
        self.calendar_window.title("Seleccionar Fecha")
        self.calendar_window.geometry("280x240")  # Tamaño más compacto
        self.calendar_window.resizable(False, False)
        
        # Posicionar la ventana justo debajo del botón del calendario
        self.calendar_window.transient(self.winfo_toplevel())
        self.calendar_window.grab_set()
        
        # Calcular posición relativa al botón del calendario
        self.update_idletasks()  # Asegurar que todo esté renderizado
        
        # Obtener posición absoluta del botón del calendario
        btn_x = self.calendar_btn.winfo_rootx()
        btn_y = self.calendar_btn.winfo_rooty()
        btn_height = self.calendar_btn.winfo_height()
        
        # Posicionar el calendario debajo del botón, ajustando hacia la izquierda
        calendar_x = btn_x - 220  # Ajustado para el nuevo ancho más pequeño
        calendar_y = btn_y + btn_height + 5  # 5px de margen debajo del botón
        
        # Asegurar que no se salga de la pantalla
        screen_width = self.calendar_window.winfo_screenwidth()
        screen_height = self.calendar_window.winfo_screenheight()
        
        # Ajustar si se sale por la derecha
        if calendar_x + 280 > screen_width:
            calendar_x = screen_width - 280 - 10
        
        # Ajustar si se sale por la izquierda
        if calendar_x < 10:
            calendar_x = 10
        
        # Ajustar si se sale por abajo
        if calendar_y + 240 > screen_height:
            calendar_y = btn_y - 240 - 5  # Mostrar arriba del botón
        
        # Aplicar la posición calculada
        self.calendar_window.geometry(f"280x240+{calendar_x}+{calendar_y}")
        
        # Obtener fecha actual o fecha seleccionada
        try:
            if self.date_entry.get():
                selected = datetime.strptime(self.date_entry.get(), "%d/%m/%Y")
                year, month = selected.year, selected.month
            else:
                today = date.today()
                year, month = today.year, today.month
        except:
            today = date.today()
            year, month = today.year, today.month
        
        # Crear el calendario
        calendar_frame = tk.Frame(self.calendar_window, **theme_manager.get_style("frame"))
        calendar_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Header con navegación más compacto
        header_frame = tk.Frame(calendar_frame, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, 8))
        
        # Botón anterior
        prev_btn = tk.Button(
            header_frame,
            text="◀",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=2,
            height=1,
            cursor="hand2",
            command=self._prev_month
        )
        prev_btn.pack(side="left")
        
        # Label del mes (sin conflicto de font)
        self.month_label = tk.Label(
            header_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=("Segoe UI", 11, "bold"),
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        
        # Botón siguiente
        next_btn = tk.Button(
            header_frame,
            text="▶",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=2,
            height=1,
            cursor="hand2",
            command=self._next_month
        )
        next_btn.pack(side="right")
        
        # Frame para el grid del calendario (compacto)
        self.cal_frame = tk.Frame(calendar_frame, **theme_manager.get_style("frame"))
        self.cal_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        # Variables para el calendario - IMPORTANTE: inicializar aquí
        self.current_month = month
        self.current_year = year
        
        # Crear el calendario inicial
        self._create_calendar()
        
        # Botones de acción en la parte inferior más compactos
        buttons_frame = tk.Frame(calendar_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(fill="x")
        
        # Botón "Hoy"
        today_btn = tk.Button(
            buttons_frame,
            text="Hoy",
            font=("Segoe UI", 9),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_primary_bg"],
            fg="white",
            bd=0,
            relief="solid",
            width=6,
            height=1,
            cursor="hand2",
            command=self._select_today
        )
        today_btn.pack(side="left")
        
        # Botón "Cerrar"
        close_btn = tk.Button(
            buttons_frame,
            text="Cerrar",
            font=("Segoe UI", 9),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=6,
            height=1,
            cursor="hand2",
            command=self._close_calendar
        )
        close_btn.pack(side="right")
    
    def _create_calendar(self):
        """Crea el grid del calendario"""
        # Limpiar frame actual
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
        
        # Actualizar label del mes
        self.month_label.configure(text=f"{calendar.month_name[self.current_month]} {self.current_year}")
        
        # Configurar el grid para que se expanda uniformemente pero compacto
        for i in range(7):  # 7 columnas (días de la semana)
            self.cal_frame.grid_columnconfigure(i, weight=1, uniform="day")
        
        # Días de la semana más compactos
        days = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
        for i, day in enumerate(days):
            label = tk.Label(
                self.cal_frame,
                text=day,
                font=("Segoe UI", 8, "bold"),
                bg=theme_manager.themes[theme_manager.current_theme]["bg_secondary"],
                fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
                width=3,
                height=1
            )
            label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
        
        # Obtener el calendario del mes
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Configurar filas del grid más compactas
        for week_num in range(1, len(cal) + 1):
            self.cal_frame.grid_rowconfigure(week_num, weight=1, uniform="week")
        
        # Crear botones para cada día más pequeños
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Día vacío
                    label = tk.Label(
                        self.cal_frame, 
                        text="", 
                        width=3, 
                        height=1,
                        bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
                    )
                    label.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
                else:
                    # Botón del día más compacto
                    btn = tk.Button(
                        self.cal_frame,
                        text=str(day),
                        font=("Segoe UI", 8),
                        bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
                        fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
                        bd=1,
                        relief="solid",
                        width=3,
                        height=1,
                        cursor="hand2",
                        command=lambda d=day: self._select_date(d)
                    )
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
                    
                    # Resaltar día actual
                    today = date.today()
                    if (day == today.day and 
                        self.current_month == today.month and 
                        self.current_year == today.year):
                        btn.configure(
                            bg=theme_manager.themes[theme_manager.current_theme]["btn_primary_bg"],
                            fg="white",
                            font=("Segoe UI", 8, "bold")
                        )
    
    def _prev_month(self):
        """Cambia al mes anterior"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self._create_calendar()
    
    def _next_month(self):
        """Cambia al mes siguiente"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self._create_calendar()
    
    def _select_date(self, day):
        """Selecciona una fecha específica"""
        selected_date = date(self.current_year, self.current_month, day)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, selected_date.strftime("%d/%m/%Y"))
        self.selected_date = selected_date
        self._close_calendar()
    
    def _select_today(self):
        """Selecciona la fecha de hoy"""
        today = date.today()
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today.strftime("%d/%m/%Y"))
        self.selected_date = today
        self._close_calendar()
    
    def _close_calendar(self):
        """Cierra la ventana del calendario"""
        if self.calendar_window:
            self.calendar_window.destroy()
            self.calendar_window = None
    
    def get(self):
        """Obtiene el valor de la fecha"""
        return self.date_entry.get()
    
    def set(self, value):
        """Establece el valor de la fecha"""
        self.date_entry.delete(0, tk.END)
        if value:
            self.date_entry.insert(0, str(value))

class TenantFormView(tk.Frame):
    """Formulario profesional para inquilinos"""

    def __init__(self, parent, on_back: Callable = None, tenant_data: Dict[str, Any] = None, on_save_success: Callable = None, on_navigate_to_dashboard: Callable = None, reactivate_mode: bool = False):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._form_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._form_bg)
        
        self.on_back = on_back
        self.on_save_success = on_save_success
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.tenant_data = tenant_data or {}
        self.is_edit_mode = bool(tenant_data)
        self.reactivate_mode = reactivate_mode  # Modo especial para reactivación
        self.validation_errors = {}
        
        # Variables para los campos
        self._init_form_variables()
        
        # Crear layout
        self._create_layout()
        
        # Cargar datos si es modo edición o reactivación
        if self.is_edit_mode or self.reactivate_mode:
            self._load_tenant_data()
    
    def _init_form_variables(self):
        """Inicializa las variables del formulario"""
        self.form_fields = {}

    def _get_entry_style(self):
        """Estilo unificado para campos de entrada: fondo blanco, borde sutil, tema."""
        theme = theme_manager.themes[theme_manager.current_theme]
        return {
            "bg": "white",
            "fg": theme["text_primary"],
            "font": ("Segoe UI", 10),
            "highlightthickness": 1,
            "highlightbackground": theme["border_light"],
            "highlightcolor": theme["border_medium"],
            "insertbackground": theme["text_primary"],
        }
    
    def _clear_placeholder(self, event, placeholder_text):
        """Limpia el placeholder cuando se enfoca el campo"""
        if event.widget.get() == placeholder_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg=theme_manager.themes[theme_manager.current_theme]["text_primary"])
    
    def _restore_placeholder(self, event, placeholder_text):
        """Restaura el placeholder si el campo está vacío"""
        if not event.widget.get():
            event.widget.insert(0, placeholder_text)
            event.widget.config(fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"])
    
    def _create_inline_field(self, parent, label_text, field_name, placeholder_text="", field_type="entry", values=None, width=20):
        """Crea un campo inline con label al lado izquierdo - con ancho fijo para alineación"""
        theme = theme_manager.themes[theme_manager.current_theme]
        row_frame = tk.Frame(parent, bg=self._form_bg)
        row_frame.pack(fill="x", pady=(0, 1))

        label = tk.Label(
            row_frame,
            text=label_text,
            width=20,
            anchor="w",
            bg=self._form_bg,
            fg=theme["text_primary"],
            font=("Segoe UI", 9),
        )
        label.pack(side="left", padx=(0, Spacing.SM))

        if field_type == "combobox":
            field = ttk.Combobox(
                row_frame,
                values=values or [],
                state="readonly",
                width=50,
            )
            if values:
                field.set(values[0])
        else:
            field = tk.Entry(row_frame, width=35, **self._get_entry_style())
        field.pack(side="left")
        self.form_fields[field_name] = field
        return row_frame
    
    def _create_dual_inline_field(self, parent, left_label, left_field, left_type="entry", left_values=None, 
                                 right_label="", right_field="", right_type="entry", right_values=None):
        """Crea dos campos inline en la misma fila con alineación exacta"""
        theme = theme_manager.themes[theme_manager.current_theme]
        row_frame = tk.Frame(parent, bg=self._form_bg)
        row_frame.pack(fill="x", pady=(0, 1))

        left_label_widget = tk.Label(
            row_frame,
            text=left_label,
            width=20,
            anchor="w",
            bg=self._form_bg,
            fg=theme["text_primary"],
            font=("Segoe UI", 9),
        )
        left_label_widget.pack(side="left", padx=(0, Spacing.SM))

        if left_type == "combobox":
            left_widget = ttk.Combobox(
                row_frame,
                values=left_values or [],
                state="readonly",
                width=50,
            )
            if left_values and left_field != "contacto_emergencia_parentesco":
                left_widget.set(left_values[0])
        elif left_type == "datepicker":
            left_widget = DatePickerWidget(row_frame)
            left_widget.configure(bg=self._form_bg)
            left_widget.pack_configure(ipadx=0)
            left_widget.date_entry.configure(width=32, **self._get_entry_style())
            left_widget.date_entry.configure(bg="white")
            left_widget.calendar_btn.configure(width=2)
        else:
            left_widget = tk.Entry(row_frame, width=35, **self._get_entry_style())

        left_widget.pack(side="left")
        self.form_fields[left_field] = left_widget

        spacer = tk.Frame(row_frame, width=40, bg=self._form_bg)
        spacer.pack(side="left")
        spacer.pack_propagate(False)

        if right_field:
            if right_type == "combobox":
                right_widget = ttk.Combobox(
                    row_frame,
                    values=right_values or [],
                    state="readonly",
                    width=50,
                )
                if right_values and right_field != "contacto_emergencia_parentesco":
                    right_widget.set(right_values[0])
            elif right_type == "datepicker":
                right_widget = DatePickerWidget(row_frame)
                right_widget.configure(bg=self._form_bg)
                right_widget.date_entry.configure(width=32, **self._get_entry_style())
                right_widget.date_entry.configure(bg="white")
                right_widget.calendar_btn.configure(width=2)
            else:
                right_widget = tk.Entry(row_frame, width=35, **self._get_entry_style())

            right_widget.pack(side="right")
            self.form_fields[right_field] = right_widget

            right_label_widget = tk.Label(
                row_frame,
                text=right_label,
                width=20,
                anchor="w",
                bg=self._form_bg,
                fg=theme["text_primary"],
                font=("Segoe UI", 9),
            )
            right_label_widget.pack(side="right", padx=(0, Spacing.SM))

        return row_frame
    
    def _create_layout(self):
        """Crea el layout principal del formulario"""
        self._create_header()
        # Botones abajo primero para reservar espacio y que siempre sean visibles
        self._create_action_buttons(self)
        self._create_form_content_direct()
    
    def _create_header(self):
        """Crea el header con título y navegación"""
        header_frame = tk.Frame(self, bg=self._form_bg)
        header_frame.pack(fill="x", pady=2)
        
        # Título
        if self.reactivate_mode:
            title_text = "Reactivar Inquilino"
        elif self.is_edit_mode:
            title_text = "Editar Inquilino"
        else:
            title_text = "Nuevo Inquilino"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 14, "bold"), bg=self._form_bg)
        title_label.pack(side="left", pady=0)
        
        buttons_frame = tk.Frame(header_frame, bg=self._form_bg)
        buttons_frame.pack(side="right")
        
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
        # Colores azules para módulo de inquilinos
        colors = get_module_colors("inquilinos")
        blue_primary = colors["primary"]
        blue_hover = colors["hover"]
        blue_light = colors["light"]
        blue_text = colors["text"]
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard)
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if self.on_navigate_to_dashboard:
                try:
                    self.on_navigate_to_dashboard()
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar MainWindow a través de la jerarquía de widgets
            widget = self.master
            max_depth = 10
            depth = 0
            
            while widget and depth < max_depth:
                # Verificar si es MainWindow (tiene _navigate_to y _load_view)
                if (hasattr(widget, '_navigate_to') and 
                    hasattr(widget, '_load_view') and 
                    hasattr(widget, 'views_container')):
                    try:
                        widget._navigate_to("dashboard")
                        return
                    except Exception as e:
                        print(f"Error al navegar: {e}")
                        break
                
                # Subir en la jerarquía
                widget = getattr(widget, 'master', None)
                depth += 1
            
            # Prioridad 3: Buscar desde el root window
            try:
                root = self.winfo_toplevel()
                # Buscar MainWindow entre los hijos del root
                for child in root.winfo_children():
                    if (hasattr(child, '_navigate_to') and 
                        hasattr(child, '_load_view') and 
                        hasattr(child, 'views_container')):
                        child._navigate_to("dashboard")
                        return
            except Exception as e:
                print(f"Error en búsqueda desde root: {e}")
            
            # Si todo falla, mostrar mensaje
            print("No se pudo encontrar MainWindow para navegar al dashboard")
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            buttons_frame,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=blue_primary,
            hover_bg=blue_light,
            hover_fg=blue_text,
            command=self._on_back_clicked,
            padx=16,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard"
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
    
    def _create_form_content_direct(self):
        """Crea el contenido del formulario directamente sin scroll"""
        main_container = tk.Frame(self, bg=self._form_bg)
        main_container.pack(fill="both", expand=True, padx=Spacing.SM, pady=0)

        self._create_personal_info_section(main_container)
        self._create_housing_info_section(main_container)
        self._create_emergency_contact_section(main_container)
        self._create_documents_section(main_container)
    
    def _create_separator(self, parent):
        """Separador visual entre secciones"""
        theme = theme_manager.themes[theme_manager.current_theme]
        separator_frame = tk.Frame(parent, bg=self._form_bg)
        separator_frame.pack(fill="x", pady=2)
        line = tk.Frame(separator_frame, height=1, bg=theme["border_light"])
        line.pack(fill="x")

    def _create_section_header(self, parent, icon: str, title: str):
        """Encabezado de sección con barra lateral de acento (módulo inquilinos)"""
        colors = get_module_colors("inquilinos")
        theme = theme_manager.themes[theme_manager.current_theme]
        header_frame = tk.Frame(parent, bg=self._form_bg)
        header_frame.pack(fill="x", pady=(4, 0))
        # Barra vertical de acento
        accent_bar = tk.Frame(header_frame, width=3, bg=colors["primary"])
        accent_bar.pack(side="left", fill="y", padx=(0, Spacing.SM))
        accent_bar.pack_propagate(False)
        title_label = tk.Label(
            header_frame,
            text=f"{icon}  {title}",
            bg=self._form_bg,
            fg=theme["text_primary"],
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        title_label.pack(side="left")
    
    def _create_personal_info_section(self, parent):
        """Crea la sección de información personal"""
        self._create_section_header(parent, Icons.TENANT_PROFILE, "Información Personal")
        
        # Nombre completo - layout inline con ancho estándar
        self._create_inline_field(parent, "Nombre Completo *", "nombre", "")
        
        # Fila de documentos - usando la nueva función dual
        self._create_dual_inline_field(
            parent,
            "Tipo de Documento *", "tipo_documento", "combobox", 
            ["Cédula de Ciudadanía", "Cédula de Extranjería", "Pasaporte"],
            "Número de Documento *", "numero_documento"
        )
        
        # Fila de contacto - usando la nueva función dual
        self._create_dual_inline_field(
            parent,
            "Teléfono *", "telefono", "entry", None,
            "Email", "email"
        )
    
    def _create_housing_info_section(self, parent):
        """Crea la sección de información de vivienda"""
        self._create_section_header(parent, Icons.TENANT_ADDRESS, "Información de Vivienda")

        apt_row = tk.Frame(parent, bg=self._form_bg)
        apt_row.pack(fill="x", pady=(0, 1))
        theme = theme_manager.themes[theme_manager.current_theme]
        colors = get_module_colors("inquilinos")
        tk.Label(
            apt_row,
            text="Número de Apartamento *",
            bg=self._form_bg,
            fg=theme["text_primary"],
            font=("Segoe UI", 9),
            width=22,
            anchor="w",
        ).pack(side="left")
        self.selected_apartment_var = tk.StringVar()
        self.selected_apartment_id = None
        self.selected_building_id = None
        self.selected_building_name = None
        self.apt_display = tk.Entry(
            apt_row,
            textvariable=self.selected_apartment_var,
            state="readonly",
            width=32,
            **self._get_entry_style(),
        )
        self.apt_display.configure(bg="white")
        self.apt_display.pack(side="left", padx=(0, 4))
        select_btn = create_rounded_button(
            apt_row,
            text="Seleccionar...",
            bg_color=colors["light"],
            fg_color=colors["text"],
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._open_apartment_selector_modal,
            padx=12,
            pady=6,
            radius=4,
        )
        select_btn.pack(side="left")

        # Fila 1: Valor arriendo
        self._create_inline_field(parent, "Valor Arriendo *", "valor_arriendo")

        # Fila 2: Fechas - usando función dual con datepicker
        self._create_dual_inline_field(
            parent,
            "Fecha de Ingreso *", "fecha_ingreso", "datepicker", None,
            "Fecha Fin Contrato", "fecha_fin_contrato", "datepicker"
        )
        
        # Establecer la fecha actual como valor por defecto para fecha de ingreso
        if not self.is_edit_mode and 'fecha_ingreso' in self.form_fields:
            current_date = datetime.now().strftime("%d/%m/%Y")
            self.form_fields['fecha_ingreso'].set(current_date)

        # Fila 3: Estado y depósito - usando función dual
        self._create_dual_inline_field(
            parent,
            "Depósito", "deposito", "entry", None,
            "", "", "entry"  # Campo vacío para mantener el layout
        )
    
    def _open_apartment_selector_modal(self):
        from manager.app.services.apartment_service import apartment_service
        apartment_service.reload_data()
        selector = ApartmentSelectorModal(self)
        if selector.result:
            # Actualizar el campo con el formato Edificio - Tipo/Número
            self.selected_apartment_var.set(f"{selector.result['building_name']} - {selector.result['display']}")
            self.selected_apartment_id = selector.result['apartment_id']
            self.selected_building_id = selector.result['building_id']
            self.selected_building_name = selector.result['building_name']
            
            # Obtener el valor base del apartamento seleccionado y mostrarlo en el campo de arriendo
            apartment = apartment_service.get_apartment_by_id(self.selected_apartment_id)
            if apartment and apartment.get('base_rent'):
                base_rent = apartment.get('base_rent')
                # Actualizar el campo de valor de arriendo con el valor base
                if hasattr(self, 'form_fields') and 'valor_arriendo' in self.form_fields:
                    self.form_fields['valor_arriendo'].delete(0, tk.END)
                    self.form_fields['valor_arriendo'].insert(0, base_rent)
    
    def _create_emergency_contact_section(self, parent):
        """Crea la sección de contacto de emergencia"""
        self._create_section_header(parent, Icons.EMERGENCY_CONTACT, "Contacto de Emergencia")
        
        # Fila 1: Nombre y parentesco - usando función dual
        self._create_dual_inline_field(
            parent,
            "Nombre Completo", "contacto_emergencia_nombre", "entry", None,
            "Parentesco", "contacto_emergencia_parentesco", "combobox",
            ["Seleccione uno", "Padre", "Madre", "Hermano/a", "Hijo/a", "Cónyuge", "Amigo/a", "Otro"]
        )
        
        # Teléfono contacto - layout inline (ancho completo) con ancho estándar
        self._create_inline_field(parent, "Teléfono", "contacto_emergencia_telefono", "")
    
    def _create_documents_section(self, parent):
        """Crea la sección de documentos"""
        self._create_section_header(parent, Icons.TENANT_DOCUMENTS, "Documentos")

        docs_row = tk.Frame(parent, bg=self._form_bg)
        docs_row.pack(fill="x")

        theme = theme_manager.themes[theme_manager.current_theme]
        colors = get_module_colors("inquilinos")

        doc_id_frame = tk.Frame(docs_row, bg=self._form_bg)
        doc_id_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))

        tk.Label(
            doc_id_frame,
            text="Documento de Identidad",
            bg=self._form_bg,
            fg=theme["text_primary"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 1))

        doc_id_buttons = tk.Frame(doc_id_frame, bg=self._form_bg)
        doc_id_buttons.pack(fill="x")

        self.btn_upload_id = create_rounded_button(
            doc_id_buttons,
            text=f"{Icons.UPLOAD}  Seleccionar",
            bg_color=colors["light"],
            fg_color=colors["text"],
            hover_bg=colors["hover"],
            hover_fg="white",
            command=lambda: self._upload_document("id"),
            padx=10,
            pady=5,
            radius=4,
        )
        self.btn_upload_id.pack(side="left", padx=(0, Spacing.XS))

        self.id_file_label = tk.Label(
            doc_id_buttons,
            text="No seleccionado",
            bg=self._form_bg,
            fg=theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        self.id_file_label.pack(side="left")

        contract_frame = tk.Frame(docs_row, bg=self._form_bg)
        contract_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))

        tk.Label(
            contract_frame,
            text="Contrato de Arrendamiento",
            bg=self._form_bg,
            fg=theme["text_primary"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 1))

        contract_buttons = tk.Frame(contract_frame, bg=self._form_bg)
        contract_buttons.pack(fill="x")

        self.btn_upload_contract = create_rounded_button(
            contract_buttons,
            text=f"{Icons.UPLOAD}  Seleccionar",
            bg_color=colors["light"],
            fg_color=colors["text"],
            hover_bg=colors["hover"],
            hover_fg="white",
            command=lambda: self._upload_document("contract"),
            padx=10,
            pady=5,
            radius=4,
        )
        self.btn_upload_contract.pack(side="left", padx=(0, Spacing.XS))

        self.contract_file_label = tk.Label(
            contract_buttons,
            text="No seleccionado",
            bg=self._form_bg,
            fg=theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        self.contract_file_label.pack(side="left")
        
        # Variables para archivos
        self.selected_files = {
            "id": None,
            "contract": None
        }
    
    def _create_action_buttons(self, parent):
        """Crea los botones de acción del formulario"""
        theme = theme_manager.themes[theme_manager.current_theme]
        colors = get_module_colors("inquilinos")
        actions_frame = tk.Frame(parent, bg=self._form_bg)
        actions_frame.pack(fill="x", side="bottom", pady=(4, 0))

        ModernSeparator(actions_frame)

        buttons_frame = tk.Frame(actions_frame, bg=self._form_bg)
        buttons_frame.pack(pady=(2, 0))

        btn_cancel = create_rounded_button(
            buttons_frame,
            text=f"{Icons.CANCEL}  Cancelar",
            bg_color=theme["bg_secondary"],
            fg_color=theme["text_primary"],
            hover_bg=theme["bg_tertiary"],
            hover_fg=theme["text_primary"],
            command=self._on_back_clicked,
            padx=16,
            pady=8,
            radius=4,
        )
        btn_cancel.pack(side="right", padx=(Spacing.SM, 0))

        if self.reactivate_mode:
            save_text = "Reactivar"
            save_bg = colors["primary"]
            save_fg = "white"
            save_hover = colors["hover"]
        elif self.is_edit_mode:
            save_text = "Actualizar"
            save_bg = colors["primary"]
            save_fg = "white"
            save_hover = colors["hover"]
        else:
            save_text = "Guardar"
            save_bg = colors["primary"]
            save_fg = "white"
            save_hover = colors["hover"]

        btn_save = create_rounded_button(
            buttons_frame,
            text=f"{Icons.SAVE}  {save_text}",
            bg_color=save_bg,
            fg_color=save_fg,
            hover_bg=save_hover,
            hover_fg="white",
            command=self._save_tenant,
            padx=18,
            pady=8,
            radius=4,
        )
        btn_save.pack(side="right")

        required_label = tk.Label(
            buttons_frame,
            text="* Campos requeridos",
            bg=self._form_bg,
            fg=theme["text_secondary"],
            font=("Segoe UI", 10),
        )
        required_label.pack(side="left")
    
    # Métodos de funcionalidad
    def _load_tenant_data(self):
        """Carga los datos del inquilino en modo edición"""
        if not self.tenant_data:
            return
        # Mapear datos a campos
        field_mapping = {
            'nombre': 'nombre',
            'numero_documento': 'numero_documento', 
            'telefono': 'telefono',
            'email': 'email',
            'apartamento': 'apartamento',
            'valor_arriendo': 'valor_arriendo',
            'fecha_ingreso': 'fecha_ingreso',
            'estado_pago': 'estado_pago',
            'deposito': 'deposito',
            'contacto_emergencia_nombre': 'contacto_emergencia_nombre',
            'contacto_emergencia_telefono': 'contacto_emergencia_telefono',
            'contacto_emergencia_parentesco': 'contacto_emergencia_parentesco'
        }
        for field_key, data_key in field_mapping.items():
            if field_key in self.form_fields and data_key in self.tenant_data:
                value = self.tenant_data[data_key]
                # Formatear valor de arriendo y depósito
                if field_key in ['valor_arriendo', 'deposito']:
                    value = str(value)
                widget = self.form_fields[field_key]
                # Si es combobox (tiene .set), usar set
                if hasattr(widget, 'set') and not isinstance(widget, tk.Entry):
                    # Manejo especial para el parentesco del contacto de emergencia
                    if field_key == 'contacto_emergencia_parentesco':
                        if not value or value.strip() == "":
                            widget.set("Seleccione uno")
                        else:
                            widget.set(str(value))
                    else:
                        widget.set(str(value))
                # Si es Entry, usar delete/insert
                elif isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value))
        # Cargar display amigable del apartamento y setear el ID interno
        apt_id = self.tenant_data.get('apartamento')
        print(f"[DEBUG] apt_id en tenant_data: {apt_id}")
        self.selected_apartment_id = None
        self.selected_building_id = None
        self.selected_building_name = None
        if apt_id:
            try:
                from manager.app.services.apartment_service import apartment_service
                from manager.app.services.building_service import building_service
                apt_id_int = int(apt_id)
                apt = apartment_service.get_apartment_by_id(apt_id_int)
                print(f"[DEBUG] apartment_service.get_apartment_by_id({apt_id_int}): {apt}")
                if apt:
                    building = building_service.get_building_by_id(apt.get('building_id'))
                    building_name = building.get('name') if building else ''
                    tipo = apt.get('unit_type', 'Apartamento Estándar')
                    numero = apt.get('number', '')
                    if building_name:
                        display = f"{building_name} - {tipo} {numero}" if tipo != 'Apartamento Estándar' else f"{building_name} - {numero}"
                    else:
                        display = f"{tipo} {numero}" if tipo != 'Apartamento Estándar' else str(numero)
                    print(f"[DEBUG] display generado: {display}")
                    self.selected_apartment_var.set(display)
                    self.selected_apartment_id = apt_id_int
                    self.selected_building_id = apt.get('building_id')
                    self.selected_building_name = building_name
                else:
                    print("[DEBUG] No se encontró el apartamento con ese ID.")
                    self.selected_apartment_var.set("")
            except Exception as e:
                print(f"[DEBUG] Excepción al buscar apartamento: {e}")
                self.selected_apartment_var.set("")
        
        # Cargar archivos existentes
        archivos = self.tenant_data.get("archivos", {})
        if isinstance(archivos, str):
            try:
                import json
                archivos = json.loads(archivos)
            except:
                archivos = {}
        
        if archivos:
            # Cargar documento de identidad
            doc_id = archivos.get("id")
            if doc_id and str(doc_id).strip():
                self.selected_files["id"] = doc_id
                import os
                filename = os.path.basename(str(doc_id))
                self.id_file_label.configure(text=filename)
            
            # Cargar contrato
            doc_contract = archivos.get("contract")
            if doc_contract and str(doc_contract).strip():
                self.selected_files["contract"] = doc_contract
                import os
                filename = os.path.basename(str(doc_contract))
                self.contract_file_label.configure(text=filename)
    
    def _upload_document(self, doc_type: str):
        """Maneja la subida de documentos"""
        filetypes = [
            ("Archivos PDF", "*.pdf"),
            ("Imágenes", "*.jpg *.jpeg *.png"),
            ("Todos los archivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title=f"Seleccionar {doc_type}",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_files[doc_type] = filename
            
            # Actualizar label
            file_name = os.path.basename(filename)
            if doc_type == "id":
                self.id_file_label.configure(text=file_name)
            else:
                self.contract_file_label.configure(text=file_name)
    
    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario"""
        self.validation_errors = {}
        required_fields = {
            'nombre': 'Nombre completo',
            'numero_documento': 'Número de documento',
            'telefono': 'Teléfono',
            'apartamento': 'Apartamento',
            'valor_arriendo': 'Valor del arriendo',
            'fecha_ingreso': 'Fecha de ingreso'
        }
        for field, label in required_fields.items():
            if field == 'apartamento':
                value = self.selected_apartment_id or (self.selected_apartment_var.get().strip() if getattr(self, 'selected_apartment_var', None) and self.selected_apartment_var.get() else None)
            else:
                value = self.form_fields[field].get()
            if isinstance(value, str):
                value = value.strip()
            if not value:
                self.validation_errors[field] = f"{label} es requerido"
        # Validaciones específicas
        if 'telefono' not in self.validation_errors:
            phone = self.form_fields['telefono'].get()
            if isinstance(phone, str):
                phone = phone.strip()
            if not re.match(r'^\+?[\d\s\-\(\)]+$', phone):
                self.validation_errors['telefono'] = "Formato de teléfono inválido"
        if 'email' not in self.validation_errors:
            email = self.form_fields['email'].get()
            if isinstance(email, str):
                email = email.strip()
            if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                self.validation_errors['email'] = "Formato de email inválido"
        if 'valor_arriendo' not in self.validation_errors:
            rent = self.form_fields['valor_arriendo'].get()
            if isinstance(rent, str):
                rent = rent.strip()
            try:
                float(rent)
            except ValueError:
                self.validation_errors['valor_arriendo'] = "El valor debe ser numérico"
        if 'fecha_ingreso' not in self.validation_errors:
            fecha_ingreso = self.form_fields['fecha_ingreso'].get()
            if isinstance(fecha_ingreso, str):
                fecha_ingreso = fecha_ingreso.strip()
            if fecha_ingreso and not self._validate_date(fecha_ingreso):
                self.validation_errors['fecha_ingreso'] = "Formato de fecha inválido (DD/MM/AAAA)"
        optional_date_fields = ['fecha_fin_contrato']
        for field in optional_date_fields:
            if field in self.form_fields:
                date_value = self.form_fields[field].get()
                if isinstance(date_value, str):
                    date_value = date_value.strip()
                if date_value and not self._validate_date(date_value):
                    self.validation_errors[field] = "Formato de fecha inválido (DD/MM/AAAA)"
        return len(self.validation_errors) == 0
    
    def _validate_date(self, date_str: str) -> bool:
        """Valida formato de fecha DD/MM/AAAA"""
        if not date_str.strip():
            return True  # Fechas vacías son válidas para campos opcionales
            
        try:
            # Intentar varios formatos de fecha
            formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]
            for fmt in formats:
                try:
                    datetime.strptime(date_str.strip(), fmt)
                    return True
                except ValueError:
                    continue
            return False
        except Exception:
            return False
    
    def _save_tenant(self):
        """Guarda o actualiza el inquilino"""
        required_fields = {
            'nombre': 'Nombre completo',
            'numero_documento': 'Número de documento',
            'telefono': 'Teléfono',
            'apartamento': 'Apartamento',
            'valor_arriendo': 'Valor del arriendo',
            'fecha_ingreso': 'Fecha de ingreso'
        }
        self.validation_errors = {}
        for field, label in required_fields.items():
            if field in self.form_fields:
                value = self.form_fields[field].get()
                if isinstance(value, str):
                    value = value.strip()
                if not value:
                    self.validation_errors[field] = f"{label} es requerido"
            elif field == 'apartamento':
                if not self.selected_apartment_id and not (getattr(self, 'selected_apartment_var', None) and self.selected_apartment_var.get() and self.selected_apartment_var.get().strip()):
                    self.validation_errors[field] = f"{label} es requerido"
        if 'fecha_ingreso' in self.form_fields and 'fecha_ingreso' not in self.validation_errors:
            date_str = self.form_fields['fecha_ingreso'].get()
            if isinstance(date_str, str):
                date_str = date_str.strip()
            if not self._validate_date(date_str):
                self.validation_errors['fecha_ingreso'] = "Formato de fecha inválido (DD/MM/AAAA)"
        if 'valor_arriendo' in self.form_fields and 'valor_arriendo' not in self.validation_errors:
            try:
                valor = self.form_fields['valor_arriendo'].get()
                if isinstance(valor, str):
                    valor = valor.strip().replace(',', '')
                valor = float(valor)
                if valor <= 0:
                    self.validation_errors['valor_arriendo'] = "El valor del arriendo debe ser mayor a 0"
            except ValueError:
                self.validation_errors['valor_arriendo'] = "El valor del arriendo debe ser numérico"
        if self.validation_errors:
            self._show_validation_errors()
            return
        tenant_data = self._collect_form_data()
        tenant_data.setdefault('archivos', {})
        tenant_data.setdefault('has_documents', False)
        
        try:
            from manager.app.services.apartment_service import apartment_service
            
            if self.reactivate_mode:
                # Modo reactivación: actualizar datos y reactivar
                tenant_id = self.tenant_data.get("id")
                
                # Actualizar los datos del inquilino
                result = tenant_service.update_tenant(tenant_id, tenant_data)
                
                # Eliminar campos de desactivación y cambiar estado
                tenant_service._load_data()
                for i, t in enumerate(tenant_service.tenants):
                    if t.get("id") == tenant_id:
                        # Eliminar las claves de desactivación si existen
                        if "motivo_desactivacion" in tenant_service.tenants[i]:
                            del tenant_service.tenants[i]["motivo_desactivacion"]
                        if "fecha_desactivacion" in tenant_service.tenants[i]:
                            del tenant_service.tenants[i]["fecha_desactivacion"]
                        # Cambiar estado a activo
                        tenant_service.tenants[i]["estado_pago"] = "al_dia"
                        tenant_service.tenants[i]["updated_at"] = datetime.now().isoformat()
                        tenant_service._save_data()
                        break
                
                # Marcar apartamento como ocupado
                apt_id = tenant_data.get('apartamento')
                if apt_id:
                    try:
                        apt_id_int = int(apt_id) if isinstance(apt_id, str) else apt_id
                        apt = apartment_service.get_apartment_by_id(apt_id_int)
                        if apt:
                            apartment_service.update_apartment(apt_id_int, {"status": "Ocupado"})
                    except (ValueError, TypeError):
                        pass
                
                action = "reactivado"
                
            elif self.is_edit_mode:
                tenant_id = self.tenant_data.get("id")
                result = tenant_service.update_tenant(tenant_id, tenant_data)
                action = "actualizado"
            else:
                # Calcular automáticamente el estado de pago basado en el historial real
                # Para inquilinos nuevos, se establecerá como 'pendiente_registro' inicialmente
                # y se recalculará cuando se registren pagos
                tenant_data.setdefault('estado_pago', 'pendiente_registro')
                result = tenant_service.create_tenant(tenant_data)
                action = "guardado"
            
            # --- Actualizar estado del apartamento a 'Ocupado' (si no es reactivación, ya se hizo arriba) ---
            if not self.reactivate_mode:
                apt_id = tenant_data.get('apartamento')
                if apt_id:
                    apartment_service.update_apartment(apt_id, {"status": "Ocupado"})
            
            if result:
                # Obtener el número real del apartamento
                apt_id = tenant_data.get('apartamento')
                apt_number = apt_id
                if apt_id:
                    try:
                        apt_id_int = int(apt_id) if isinstance(apt_id, str) else apt_id
                        apt = apartment_service.get_apartment_by_id(apt_id_int)
                        if apt and 'number' in apt:
                            apt_number = apt['number']
                    except Exception:
                        pass
                
                # Mostrar mensaje de éxito
                if self.reactivate_mode:
                    messagebox.showinfo(
                        "Éxito",
                        f"Inquilino reactivado correctamente.\n\nNombre: {tenant_data['nombre']}\nApartamento: {apt_number}"
                    )
                else:
                    messagebox.showinfo(
                        "Éxito",
                        f"Inquilino {action} correctamente.\n\nNombre: {tenant_data['nombre']}\nApartamento: {apt_number}"
                    )
                
                # Preguntar si quiere registrar el pago (solo para inquilinos nuevos, no en reactivación)
                if not self.is_edit_mode and not self.reactivate_mode:
                    self._ask_for_payment_registration(result, apt_number)
                
                if self.on_save_success:
                    self.on_save_success()
                self._on_back_clicked()
            else:
                messagebox.showerror("Error", "No se pudo guardar el inquilino")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _ask_for_payment_registration(self, tenant_data, apt_number):
        """Pregunta al usuario si quiere registrar el pago del inquilino"""
        tenant_name = tenant_data.get('nombre', 'Inquilino')
        rent_value = tenant_data.get('valor_arriendo', '0')
        
        # Formatear el valor del arriendo para mejor presentación
        try:
            rent_formatted = f"${int(float(rent_value)):,}".replace(',', '.')
        except:
            rent_formatted = f"${rent_value}"
        
        # Crear mensaje personalizado
        message = f"""¿Deseas registrar el pago inicial de {tenant_name}?

📋 Detalles del pago:
• Inquilino: {tenant_name}
• Apartamento: {apt_number}
• Valor: {rent_formatted}
• Fecha: {datetime.now().strftime('%d/%m/%Y')}

Esto te permitirá:
✅ Registrar el pago inicial automáticamente
✅ Generar el recibo correspondiente
✅ Mantener el historial de pagos actualizado

¿Quieres proceder con el registro del pago?"""
        
        # Mostrar diálogo con opciones personalizadas
        result = messagebox.askyesno(
            "💳 Registrar Pago Inicial",
            message,
            icon='question'
        )
        
        if result:
            # Registrar el pago automáticamente
            self._register_initial_payment(tenant_data, apt_number)
        else:
            # Mostrar mensaje informativo
            messagebox.showinfo(
                "📝 Pago Pendiente",
                f"El pago de {tenant_name} quedó pendiente.\n\nPuedes registrarlo más tarde desde el módulo de Pagos."
            )
    
    def _register_initial_payment(self, tenant_data, apt_number):
        """Registra el pago inicial del inquilino automáticamente"""
        try:
            from manager.app.services.payment_service import payment_service
            
            # Preparar datos del pago usando la estructura correcta del servicio
            payment_data = {
                'id_inquilino': tenant_data.get('id'),  # ID del inquilino recién creado
                'nombre_inquilino': tenant_data.get('nombre'),
                'fecha_pago': datetime.now().strftime('%d/%m/%Y'),
                'monto': float(tenant_data.get('valor_arriendo', 0)),
                'metodo': 'Efectivo',  # Método por defecto
                'observaciones': f'Pago inicial - {tenant_data.get("nombre")} - Apartamento {apt_number}'
            }
            
            # Registrar el pago usando el método correcto
            success = payment_service.add_payment(payment_data)
            
            if success:
                # Recalcular el estado de pago del inquilino después del pago
                tenant_id = tenant_data.get('id')
                if tenant_id:
                    tenant_service.update_payment_status(tenant_id)
                
                messagebox.showinfo(
                    "✅ Pago Registrado",
                    f"Pago inicial registrado exitosamente para {tenant_data.get('nombre')}.\n\n"
                    f"💰 Monto: ${int(float(tenant_data.get('valor_arriendo', 0))):,}\n"
                    f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}\n"
                    f"🏠 Apartamento: {apt_number}\n\n"
                    f"El recibo se ha generado automáticamente."
                )
            else:
                messagebox.showwarning(
                    "⚠️ Error en Pago",
                    f"No se pudo registrar el pago automáticamente.\n\n"
                    f"Puedes registrarlo manualmente desde el módulo de Pagos."
                )
                
        except Exception as e:
            messagebox.showwarning(
                "⚠️ Error en Pago",
                f"Error al registrar el pago automáticamente:\n{str(e)}\n\n"
                f"Puedes registrarlo manualmente desde el módulo de Pagos."
            )
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila todos los datos del formulario y copia documentos a la carpeta del inquilino."""
        data = {}
        for field_name, field_widget in self.form_fields.items():
            if hasattr(field_widget, 'get'):
                value = field_widget.get()
                if isinstance(value, str):
                    value = value.strip()
                # No guardar "Seleccione uno" para el parentesco del contacto de emergencia
                if field_name == "contacto_emergencia_parentesco" and value == "Seleccione uno":
                    data[field_name] = ""
                else:
                    data[field_name] = value
        # --- Ajuste: guardar el ID real del apartamento ---
        data['apartamento'] = self.selected_apartment_id
        # Copiar documentos a documentos_inquilinos/{cedula}_{primer_nombre}/ y guardar rutas relativas
        if hasattr(self, 'selected_files'):
            data['archivos'] = self._build_archivos_and_copy(data)
        else:
            data['archivos'] = {"id": None, "contract": None}
        return data

    def _build_archivos_and_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Copia los archivos seleccionados a la carpeta del inquilino y devuelve archivos con rutas relativas."""
        archivos = {"id": None, "contract": None}
        folder_name = get_tenant_document_folder_name(data)
        ensure_dirs()
        tenant_dir = DOCUMENTOS_INQUILINOS_DIR / folder_name
        tenant_dir.mkdir(parents=True, exist_ok=True)
        for key, dest_name in (("id", "cedula.pdf"), ("contract", "contrato.pdf")):
            src = self.selected_files.get(key) if hasattr(self, 'selected_files') else None
            if not src or not str(src).strip():
                continue
            src_path = os.path.normpath(str(src))
            if not os.path.isabs(src_path):
                archivos[key] = src
                continue
            if not os.path.isfile(src_path):
                continue
            dest_path = tenant_dir / dest_name
            try:
                shutil.copy2(src_path, str(dest_path))
                archivos[key] = f"{folder_name}/{dest_name}"
            except Exception as e:
                messagebox.showwarning("Documentos", f"No se pudo copiar {dest_name}: {e}")
        return archivos
    
    def _show_validation_errors(self):
        """Muestra los errores de validación"""
        if not self.validation_errors:
            return
        
        error_msg = "Por favor corrija los siguientes errores:\n\n"
        for field, error in self.validation_errors.items():
            error_msg += f"• {error}\n"
        
        messagebox.showerror("Errores de validación", error_msg)
    
    def _on_back_clicked(self):
        """Maneja el clic en volver"""
        if self.on_back:
            self.on_back()

# --- MODAL DE SELECCIÓN DE APARTAMENTO ---
class ApartmentSelectorModal(tk.Toplevel):
    MAX_UNITS_PER_ROW = 4  # Unidades por fila para layout simétrico

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Seleccionar Apartamento")
        self.minsize(400, 400)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.selected_btn = None
        self.selected_info = None
        self._build_ui()
        self._center_and_resize()
        self.wait_window(self)

    def _center_and_resize(self):
        """Centra la ventana y la amplía hasta justo encima de la barra de tareas."""
        self.update_idletasks()
        win_w = 540
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        # Margen generoso para barra de tareas y espacio visual (ventana completa y proporcionada)
        margin_bottom = 150
        win_h = max(400, min(screen_h - margin_bottom, 880))
        x = max(0, (screen_w - win_w) // 2)
        y = max(0, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")

    def _build_ui(self):
        from manager.app.services.building_service import building_service
        from manager.app.services.apartment_service import apartment_service
        from manager.app.ui.components.theme_manager import theme_manager
        # Título fijo arriba
        tk.Label(self, text="Selecciona un apartamento o unidad:", font=("Segoe UI", 13, "bold")).pack(pady=(10, 6))
        # Área con scroll para que se vean todos los pisos y no se corte la ventana
        scroll_container = tk.Frame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        canvas = tk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas)
        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_win_id, width=e.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        buildings = building_service.get_all_buildings()
        apartments = apartment_service.get_all_apartments()
        apts_by_building = {}
        for b in buildings:
            apts_by_building[b['id']] = [a for a in apartments if a.get('building_id') == b['id']]
        for b in buildings:
            b_frame = tk.LabelFrame(inner_frame, text=b['name'], font=("Segoe UI", 11, "bold"), padx=10, pady=10)
            b_frame.pack(fill="x", padx=10, pady=(0, 10))
            apts = apts_by_building.get(b['id'], [])
            def _sort_floor(x):
                s = str(x)
                return (0, int(s)) if s.isdigit() else (1, s)
            pisos = sorted(set(a.get('floor') for a in apts if a.get('floor') is not None), key=_sort_floor)
            for piso in pisos:
                piso_frame = tk.Frame(b_frame)
                piso_frame.pack(fill="x", pady=4)
                tk.Label(piso_frame, text=f"Piso {piso}", font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
                row = tk.Frame(piso_frame)
                row.pack(fill="x")
                apts_piso = [a for a in apts if str(a.get('floor')) == str(piso)]
                for col in range(self.MAX_UNITS_PER_ROW):
                    row.grid_columnconfigure(col, weight=1, uniform="apt")
                for i, apt in enumerate(apts_piso):
                    row_idx = i // self.MAX_UNITS_PER_ROW
                    col_idx = i % self.MAX_UNITS_PER_ROW
                    row.grid_rowconfigure(row_idx, weight=0)
                    estado = apt.get('status', 'Disponible')
                    tipo = apt.get('unit_type', 'Apartamento Estándar')
                    display = f"{tipo} {apt.get('number','')}" if tipo != 'Apartamento Estándar' else str(apt.get('number',''))
                    color = "#43a047" if estado == "Disponible" else ("#e53935" if estado == "Ocupado" else "#bdbdbd")
                    btn = tk.Button(row, text=display, width=12, height=2, bg=color, fg="white", font=("Segoe UI", 9, "bold"), relief="raised")
                    btn['state'] = "normal" if estado == "Disponible" else "disabled"
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="ew")
                    if estado == "Disponible":
                        # Capturar también el botón actual en la lambda para evitar que
                        # todas las selecciones apunten al último botón creado (p. ej. Penthouse).
                        btn.bind(
                            "<Button-1>",
                            lambda e, apt=apt, b=b, d=display, btn=btn: self._select_apartment(apt, b, d, btn),
                        )
        # Botón Cancelar fijo abajo con espacio suficiente para que se vea completo
        action_frame = tk.Frame(self)
        action_frame.pack(side="bottom", fill="x", pady=(12, 20), padx=14)
        tk.Button(action_frame, text="Cancelar", command=self.destroy, width=12).pack(side="right", padx=10)

    def _select_apartment(self, apt, building, display, btn):
        if self.selected_btn:
            self.selected_btn.config(relief="raised", bg="#43a047")
        btn.config(relief="sunken", bg="#757575")
        self.selected_btn = btn
        self.result = {
            'apartment_id': apt['id'],
            'building_id': building['id'],
            'building_name': building['name'],
            'display': display
        }
        self.after(200, self.destroy) 