"""
Formulario profesional para gestión de inquilinos
Incluye validaciones, diseño moderno y manejo de estados
"""

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
    ModernBadge, ModernSeparator
)
from manager.app.services.tenant_service import tenant_service

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
        # Campo de entrada para mostrar la fecha seleccionada
        self.date_entry = tk.Entry(self, **theme_manager.get_style("entry"))
        self.date_entry.pack(side="left", fill="x", expand=True)
        
        # Botón para abrir el calendario
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
    
    def __init__(self, parent, on_back: Callable = None, tenant_data: Dict[str, Any] = None, on_save_success: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_back = on_back
        self.on_save_success = on_save_success
        self.tenant_data = tenant_data or {}
        self.is_edit_mode = bool(tenant_data)
        self.validation_errors = {}
        
        # Variables para los campos
        self._init_form_variables()
        
        # Crear layout
        self._create_layout()
        
        # Cargar datos si es modo edición
        if self.is_edit_mode:
            self._load_tenant_data()
    
    def _init_form_variables(self):
        """Inicializa las variables del formulario"""
        self.form_fields = {}
    
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
        row_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        row_frame.pack(fill="x", pady=(0, 2))
        
        # Label con fuente uniforme y más pequeña
        label = tk.Label(
            row_frame,
            text=label_text,
            width=20,  # Ancho del label
            anchor="w",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 9)  # Fuente uniforme y más pequeña
        )
        label.pack(side="left", padx=(0, Spacing.SM))
        
        # Campo con ancho uniforme para terminar en línea de alineación
        if field_type == "combobox":
            field = ttk.Combobox(
                row_frame,
                values=values or [],
                state="readonly",
                width=50  # Ajustado para alineación perfecta con textboxes
            )
            if values:
                field.set(values[0])
        else:
            field = tk.Entry(
                row_frame, 
                width=35,  # Ancho uniforme para alineación final
                **theme_manager.get_style("entry")
            )
        
        field.pack(side="left")  # Sin expand para mantener ancho fijo
        self.form_fields[field_name] = field
        
        return row_frame
    
    def _create_dual_inline_field(self, parent, left_label, left_field, left_type="entry", left_values=None, 
                                 right_label="", right_field="", right_type="entry", right_values=None):
        """Crea dos campos inline en la misma fila con alineación exacta según líneas rojas"""
        row_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        row_frame.pack(fill="x", pady=(0, 2))
        
        # Campo izquierdo - ancho uniforme para terminar en línea de alineación
        left_label_widget = tk.Label(
            row_frame,
            text=left_label,
            width=20,  # Ancho del label
            anchor="w",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 9)  # Fuente uniforme y más pequeña
        )
        left_label_widget.pack(side="left", padx=(0, Spacing.SM))
        
        if left_type == "combobox":
            left_widget = ttk.Combobox(
                row_frame,
                values=left_values or [],
                state="readonly",
                width=50  # Ajustado para alineación perfecta con textboxes
            )
            # No seleccionar automáticamente el primer elemento para el parentesco del contacto de emergencia
            if left_values and left_field != "contacto_emergencia_parentesco":
                left_widget.set(left_values[0])
        elif left_type == "datepicker":
            left_widget = DatePickerWidget(row_frame)
            # Para datepicker configurar el ancho exacto del frame contenedor
            left_widget.pack_configure(ipadx=0)  # Sin padding interno
            # Configurar el Entry interno del DatePicker para que tenga 35 caracteres
            left_widget.date_entry.configure(width=32)  # Mismo ancho que fecha fin de contrato
            # Ajustar el botón del calendario para que sea igual de pequeño que el otro
            left_widget.calendar_btn.configure(width=2)
        else:
            left_widget = tk.Entry(
                row_frame,
                width=35,  # Mismo ancho que "Nombre Completo" - confirmado
                **theme_manager.get_style("entry")
            )
        
        left_widget.pack(side="left")
        self.form_fields[left_field] = left_widget
        
        # Espaciado entre columnas para posicionar columna derecha
        spacer = tk.Frame(row_frame, width=40, **theme_manager.get_style("frame"))
        spacer.pack(side="left")
        spacer.pack_propagate(False)
        
        # Campo derecho - solo si se especifica
        if right_field:
            if right_type == "combobox":
                right_widget = ttk.Combobox(
                    row_frame,
                    values=right_values or [],
                    state="readonly",
                    width=50  # Ajustado para alineación perfecta con textboxes
                )
                # No seleccionar automáticamente el primer elemento para el parentesco del contacto de emergencia
                if right_values and right_field != "contacto_emergencia_parentesco":
                    right_widget.set(right_values[0])
            elif right_type == "datepicker":
                right_widget = DatePickerWidget(row_frame)
                # Para datepicker configurar el ancho exacto del campo de entrada
                right_widget.date_entry.configure(width=32)  # Restaurado al tamaño anterior
                # También ajustar el botón del calendario para que sea más compacto
                right_widget.calendar_btn.configure(width=2)
            else:
                right_widget = tk.Entry(
                    row_frame,
                    width=35,  # Mismo tamaño que columna izquierda
                    **theme_manager.get_style("entry")
                )
            
            right_widget.pack(side="right")  # Alineado a la derecha
            self.form_fields[right_field] = right_widget
            
            # Label derecho después del textbox
            right_label_widget = tk.Label(
                row_frame,
                text=right_label,
                width=20,  # Ancho del label derecho aumentado para mostrar texto completo
                anchor="w",
                bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
                fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
                font=("Segoe UI", 9)  # Fuente uniforme y más pequeña
            )
            right_label_widget.pack(side="right", padx=(0, Spacing.SM))
        
        return row_frame
    
    def _create_layout(self):
        """Crea el layout principal del formulario"""
        # Header con navegación - sin padding
        self._create_header()
        
        # Formulario principal directamente - sin scroll container
        self._create_form_content_direct()
        
        # Botones de acción fijos en la parte inferior
        self._create_action_buttons(self)
    
    def _create_header(self):
        """Crea el header con título y navegación"""
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=2)  # Padding mínimo
        
        # Título
        title_text = "Editar Inquilino" if self.is_edit_mode else "Nuevo Inquilino"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 14, "bold"))
        title_label.pack(side="left", pady=0)
        
        # Botón volver - movido a la derecha
        btn_back = tk.Button(
            header_frame,
            text="← Volver",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=10,
            height=1,
            padx=4,
            pady=2,
            command=self._on_back_clicked
        )
        btn_back.pack(side="right")
    
    def _create_form_content_direct(self):
        """Crea el contenido del formulario directamente sin scroll"""
        # Contenedor principal con padding ultra-mínimo
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(fill="both", expand=True, padx=2, pady=0)  # Padding horizontal ultra-reducido
        
        # Todas las secciones en una sola columna - completamente compacto
        self._create_personal_info_section(main_container)
        self._create_housing_info_section(main_container)
        self._create_emergency_contact_section(main_container)
        self._create_documents_section(main_container)
    
    def _create_separator(self, parent):
        """Crea un separador visual entre secciones"""
        separator_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        separator_frame.pack(fill="x", pady=2)  # Reducido considerablemente
        
        line = tk.Frame(
            separator_frame,
            height=1,
            bg=theme_manager.themes[theme_manager.current_theme]["border_light"]
        )
        line.pack(fill="x")
    
    def _create_personal_info_section(self, parent):
        """Crea la sección de información personal"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.TENANT_PROFILE} Información Personal",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
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
        title_label = tk.Label(
            parent,
            text=f"{Icons.TENANT_ADDRESS} Información de Vivienda",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))

        # --- Campo de apartamento con botón de selección ---
        apt_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        apt_row.pack(fill="x", pady=(0, 2))
        label_style = theme_manager.get_style("label_body").copy()
        label_style.pop("anchor", None)
        tk.Label(apt_row, text="Número de Apartamento *", **label_style, width=22, anchor="w").pack(side="left")
        self.selected_apartment_var = tk.StringVar()
        self.selected_apartment_id = None  # Guardará el id real del apartamento
        self.selected_building_id = None
        self.selected_building_name = None
        self.apt_display = tk.Entry(apt_row, textvariable=self.selected_apartment_var, state="readonly", width=32, font=("Segoe UI", 10))
        self.apt_display.pack(side="left", padx=(0, 4))
        select_btn = tk.Button(
            apt_row,
            text="Seleccionar...",
            font=("Segoe UI", 9),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            relief="solid",
            bd=1,
            padx=6,
            pady=2,
            cursor="hand2",
            command=self._open_apartment_selector_modal
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
        """Crea la sección de contacto de emergencia - layout inline compacto"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.EMERGENCY_CONTACT} Contacto de Emergencia",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
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
        """Crea la sección de documentos - diseño horizontal compacto"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.TENANT_DOCUMENTS} Documentos",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
        # Contenedor horizontal para ambos documentos
        docs_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        docs_row.pack(fill="x")
        
        # Documento de identidad (lado izquierdo)
        doc_id_frame = tk.Frame(docs_row, **theme_manager.get_style("frame"))
        doc_id_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        doc_id_label = tk.Label(
            doc_id_frame,
            text="Documento de Identidad",
            **theme_manager.get_style("label_body")
        )
        doc_id_label.pack(anchor="w", pady=(0, 2))
        
        doc_id_buttons = tk.Frame(doc_id_frame, **theme_manager.get_style("frame"))
        doc_id_buttons.pack(fill="x")
        
        self.btn_upload_id = tk.Button(
            doc_id_buttons,
            text=f"{Icons.UPLOAD} Seleccionar",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=lambda: self._upload_document("id")
        )
        self.btn_upload_id.pack(side="left", padx=(0, Spacing.XS))
        
        self.id_file_label = tk.Label(
            doc_id_buttons,
            text="No seleccionado",
            **theme_manager.get_style("label_body")
        )
        self.id_file_label.pack(side="left")
        
        # Contrato (lado derecho)
        contract_frame = tk.Frame(docs_row, **theme_manager.get_style("frame"))
        contract_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        contract_label = tk.Label(
            contract_frame,
            text="Contrato de Arrendamiento",
            **theme_manager.get_style("label_body")
        )
        contract_label.pack(anchor="w", pady=(0, 2))
        
        contract_buttons = tk.Frame(contract_frame, **theme_manager.get_style("frame"))
        contract_buttons.pack(fill="x")
        
        self.btn_upload_contract = tk.Button(
            contract_buttons,
            text=f"{Icons.UPLOAD} Seleccionar",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=lambda: self._upload_document("contract")
        )
        self.btn_upload_contract.pack(side="left", padx=(0, Spacing.XS))
        
        self.contract_file_label = tk.Label(
            contract_buttons,
            text="No seleccionado",
            **theme_manager.get_style("label_body")
        )
        self.contract_file_label.pack(side="left")
        
        # Variables para archivos
        self.selected_files = {
            "id": None,
            "contract": None
        }
    
    def _create_action_buttons(self, parent):
        """Crea los botones de acción del formulario"""
        actions_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        actions_frame.pack(fill="x", side="bottom", pady=(2, 0))
        
        # Separador
        ModernSeparator(actions_frame)
        
        # Botones
        buttons_frame = tk.Frame(actions_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=(2, 0))
        
        # Botón cancelar
        btn_cancel = tk.Button(
            buttons_frame,
            text=f"{Icons.CANCEL} Cancelar",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=self._on_back_clicked
        )
        btn_cancel.pack(side="right", padx=(Spacing.SM, 0))
        
        # Botón guardar
        save_text = "Actualizar" if self.is_edit_mode else "Guardar"
        btn_save = tk.Button(
            buttons_frame,
            text=f"{Icons.SAVE} {save_text}",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_primary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_primary_fg"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=self._save_tenant
        )
        btn_save.pack(side="right")
        
        # Mensaje de campos requeridos
        required_label = tk.Label(
            buttons_frame,
            text="* Campos requeridos",
            **theme_manager.get_style("label_body")
        )
        required_label.configure(
            fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"]
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
            file_name = filename.split("/")[-1]
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
        
        # Calcular automáticamente el estado de pago basado en el historial real
        # Para inquilinos nuevos, se establecerá como 'pendiente_registro' inicialmente
        # y se recalculará cuando se registren pagos
        tenant_data.setdefault('estado_pago', 'pendiente_registro')
        try:
            if self.is_edit_mode:
                tenant_id = self.tenant_data.get("id")
                result = tenant_service.update_tenant(tenant_id, tenant_data)
                action = "actualizado"
            else:
                result = tenant_service.create_tenant(tenant_data)
                action = "guardado"
            # --- Actualizar estado del apartamento a 'Ocupado' ---
            from manager.app.services.apartment_service import apartment_service
            apt_id = tenant_data.get('apartamento')
            if apt_id:
                apartment_service.update_apartment(apt_id, {"status": "Ocupado"})
            if result:
                # Obtener el número real del apartamento
                apt_number = apt_id
                if apt_id:
                    try:
                        apt = apartment_service.get_apartment_by_id(int(apt_id))
                        if apt and 'number' in apt:
                            apt_number = apt['number']
                    except Exception:
                        pass
                
                # Mostrar mensaje de éxito
                messagebox.showinfo(
                    "Éxito",
                    f"Inquilino {action} correctamente.\n\nNombre: {tenant_data['nombre']}\nApartamento: {apt_number}"
                )
                
                # Preguntar si quiere registrar el pago (solo para inquilinos nuevos)
                if not self.is_edit_mode:
                    self._ask_for_payment_registration(result, apt_number)
                
                if self.on_save_success:
                    self.on_save_success()
                self._on_back_clicked()
            else:
                messagebox.showerror("Error", "No se pudo guardar el inquilino")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
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
        """Recopila todos los datos del formulario"""
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
        # Agregar archivos seleccionados
        if hasattr(self, 'selected_files'):
            data['archivos'] = self.selected_files.copy()
        else:
            data['archivos'] = {"id": None, "contract": None}
        # --- Ajuste: guardar el ID real del apartamento ---
        data['apartamento'] = self.selected_apartment_id
        return data
    
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
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Seleccionar Apartamento")
        self.geometry("1050x700")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.selected_btn = None
        self.selected_info = None
        self._build_ui()
        self.wait_window(self)

    def _build_ui(self):
        from manager.app.services.building_service import building_service
        from manager.app.services.apartment_service import apartment_service
        from manager.app.ui.components.theme_manager import theme_manager
        tk.Label(self, text="Selecciona un apartamento o unidad:", font=("Segoe UI", 13, "bold")).pack(pady=10)
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        buildings = building_service.get_all_buildings()
        apartments = apartment_service.get_all_apartments()
        # Agrupar apartamentos por edificio
        apts_by_building = {}
        for b in buildings:
            apts_by_building[b['id']] = [a for a in apartments if a.get('building_id') == b['id']]
        for b in buildings:
            b_frame = tk.LabelFrame(frame, text=b['name'], font=("Segoe UI", 11, "bold"), padx=10, pady=10)
            b_frame.pack(side="left", fill="y", expand=True, padx=10)
            apts = apts_by_building.get(b['id'], [])
            # Agrupar por piso para visualización tipo matriz
            pisos = sorted(set(a.get('floor') for a in apts if a.get('floor') is not None), key=lambda x: int(x) if str(x).isdigit() else str(x))
            for piso in pisos:
                piso_frame = tk.Frame(b_frame)
                piso_frame.pack(fill="x", pady=2)
                tk.Label(piso_frame, text=f"Piso {piso}", font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
                row = tk.Frame(piso_frame)
                row.pack(fill="x")
                for apt in [a for a in apts if a.get('floor') == piso]:
                    estado = apt.get('status', 'Disponible')
                    tipo = apt.get('unit_type', 'Apartamento Estándar')
                    display = f"{tipo} {apt.get('number','')}" if tipo != 'Apartamento Estándar' else str(apt.get('number',''))
                    color = "#43a047" if estado == "Disponible" else ("#e53935" if estado == "Ocupado" else "#bdbdbd")
                    btn = tk.Button(row, text=display, width=14, height=2, bg=color, fg="white" if estado!="Disponible" else "#fff", font=("Segoe UI", 10, "bold"), relief="raised")
                    btn['state'] = "normal" if estado == "Disponible" else "disabled"
                    btn.pack(side="left", padx=3, pady=2)
                    if estado == "Disponible":
                        btn.bind("<Button-1>", lambda e, apt=apt, b=b, d=display: self._select_apartment(apt, b, d, btn))
        # Botones de acción
        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", pady=10)
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