"""
Vista completa para registrar nuevos gastos del edificio
Diseño escalable y útil para el administrador
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional, Dict, Any
from datetime import datetime, date
import calendar
import os
import shutil
from pathlib import Path

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors
from manager.app.services.expense_service import ExpenseService
from manager.app.services.apartment_service import apartment_service


class DatePickerWidget(tk.Frame):
    """Widget personalizado para selección de fechas con calendario"""
    _open_calendar_instance = None  # instancia con calendario abierto (para cerrar al clic fuera)
    _click_outside_bound = False   # si ya se enlazó el clic global una vez

    def __init__(self, parent, on_change=None, **kwargs):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.configure(bg=parent.cget("bg"))
        self.selected_date = None
        self.calendar_window = None
        self.on_change = on_change
        self._create_widget()
    
    def _create_widget(self):
        """Crea el widget de selección de fecha (ancho y altura acordes al resto de campos)."""
        theme = theme_manager.themes[theme_manager.current_theme]
        # Misma fuente que los demás campos del formulario para altura uniforme
        entry_font = ("Segoe UI", 10)
        border_grey = "#d1d5db"
        date_entry_width = 23
        entry_wrapper = tk.Frame(self, bg=border_grey, bd=0)
        entry_wrapper.pack(side="left")
        inner = tk.Frame(entry_wrapper, bg=theme.get("bg_primary", "#ffffff"))
        inner.pack(padx=1, pady=1)
        self.date_entry = tk.Entry(
            inner,
            font=entry_font,
            width=date_entry_width,
            bg=theme.get("bg_primary", "#ffffff"),
            fg=theme.get("text_primary", "#1e293b"),
            relief="flat",
            bd=0
        )
        self.date_entry.pack(pady=1, ipady=2, padx=2)
        if self.on_change:
            self.date_entry.bind("<KeyRelease>", lambda e: self._notify_change())
            self.date_entry.bind("<FocusOut>", lambda e: self._notify_change())
        # Selector de calendario inmediatamente a la derecha del campo de fecha (altura reducida)
        self.calendar_btn = tk.Button(
            self,
            text="📅",
            font=entry_font,
            bg=theme["btn_secondary_bg"],
            fg=theme["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=3,
            cursor="hand2",
            command=self._show_calendar
        )
        self.calendar_btn.pack(side="left", padx=(6, 0), pady=1, ipady=1)
    
    def _show_calendar(self):
        """Muestra el calendario en una ventana emergente"""
        if self.calendar_window:
            self.calendar_window.destroy()
        
        # Ventana del calendario (tamaño reducido, cierra al hacer clic fuera)
        cal_width, cal_height = 250, 268
        self.calendar_window = tk.Toplevel(self)
        self.calendar_window.title("Seleccionar Fecha")
        self.calendar_window.geometry(f"{cal_width}x{cal_height}")
        self.calendar_window.resizable(False, False)

        self.calendar_window.transient(self.winfo_toplevel())
        DatePickerWidget._open_calendar_instance = self
        if not DatePickerWidget._click_outside_bound:
            root = self.winfo_toplevel()
            while root.master:
                root = root.master
            root.bind_all("<Button-1>", self._on_click_anywhere)
            DatePickerWidget._click_outside_bound = True

        self.update_idletasks()
        btn_x = self.calendar_btn.winfo_rootx()
        btn_y = self.calendar_btn.winfo_rooty()
        btn_height = self.calendar_btn.winfo_height()
        screen_width = self.calendar_window.winfo_screenwidth()
        screen_height = self.calendar_window.winfo_screenheight()

        # Horizontal: alineado al botón, sin salir de pantalla
        calendar_x = btn_x - 220
        if calendar_x + cal_width > screen_width:
            calendar_x = screen_width - cal_width - 10
        if calendar_x < 10:
            calendar_x = 10

        # Vertical: abrir donde haya más espacio para que se vean Hoy/Cerrar
        margin = 10
        space_above = btn_y
        space_below = screen_height - (btn_y + btn_height)
        if space_above >= space_below and space_above >= cal_height + margin:
            calendar_y = btn_y - cal_height - 5
        else:
            calendar_y = btn_y + btn_height + 5
        if calendar_y < margin:
            calendar_y = margin
        if calendar_y + cal_height > screen_height - margin:
            calendar_y = screen_height - cal_height - margin

        self.calendar_window.geometry(f"{cal_width}x{cal_height}+{calendar_x}+{calendar_y}")
        
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
        
        # Crear el calendario (padding y fuentes compactos)
        calendar_frame = tk.Frame(self.calendar_window, **theme_manager.get_style("frame"))
        calendar_frame.pack(fill="both", expand=True, padx=6, pady=6)
        header_frame = tk.Frame(calendar_frame, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, 4))
        prev_btn = tk.Button(
            header_frame,
            text="◀",
            font=("Segoe UI", 9),
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
        
        self.month_label = tk.Label(
            header_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=("Segoe UI", 10, "bold"),
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        
        next_btn = tk.Button(
            header_frame,
            text="▶",
            font=("Segoe UI", 9),
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
        
        self.cal_frame = tk.Frame(calendar_frame, **theme_manager.get_style("frame"))
        self.cal_frame.pack(fill="both", expand=True, pady=(0, 4))
        
        # Variables para el calendario
        self.current_month = month
        self.current_year = year
        
        # Crear el calendario inicial
        self._create_calendar()
        
        # Botones de acción
        buttons_frame = tk.Frame(calendar_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(fill="x")
        
        today_btn = tk.Button(
            buttons_frame,
            text="Hoy",
            font=("Segoe UI", 8),
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
        
        close_btn = tk.Button(
            buttons_frame,
            text="Cerrar",
            font=("Segoe UI", 8),
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
        
        # Configurar el grid
        for i in range(7):
            self.cal_frame.grid_columnconfigure(i, weight=1, uniform="day")
        
        # Días de la semana
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
        
        # Configurar filas del grid
        for week_num in range(1, len(cal) + 1):
            self.cal_frame.grid_rowconfigure(week_num, weight=1, uniform="week")
        
        # Crear botones para cada día
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
                    # Botón del día
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
    
    def _notify_change(self):
        if self.on_change:
            self.on_change()

    def _select_date(self, day):
        """Selecciona una fecha específica"""
        selected_date = date(self.current_year, self.current_month, day)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, selected_date.strftime("%d/%m/%Y"))
        self.selected_date = selected_date
        self._close_calendar()
        self._notify_change()

    def _select_today(self):
        """Selecciona la fecha de hoy"""
        today = date.today()
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today.strftime("%d/%m/%Y"))
        self.selected_date = today
        self._close_calendar()
        self._notify_change()
    
    def _close_calendar(self):
        """Cierra la ventana del calendario"""
        if self.calendar_window:
            DatePickerWidget._open_calendar_instance = None
            self.calendar_window.destroy()
            self.calendar_window = None

    def _on_click_anywhere(self, event):
        """Si hay un calendario abierto y el clic fue fuera de él, cerrarlo."""
        inst = DatePickerWidget._open_calendar_instance
        if not inst or not inst.calendar_window or not inst.calendar_window.winfo_exists():
            return
        try:
            w = event.widget
            while w:
                if w == inst.calendar_window:
                    return
                w = w.master if hasattr(w, "master") else None
        except Exception:
            return
        inst._close_calendar()

    def get(self):
        """Obtiene el valor de la fecha"""
        return self.date_entry.get()
    
    def set(self, value):
        """Establece el valor de la fecha"""
        self.date_entry.delete(0, tk.END)
        if value:
            self.date_entry.insert(0, str(value))


class RegisterExpenseView(tk.Frame):
    """Vista profesional para registrar nuevos gastos del edificio"""
    
    # Categorías y subtipos predefinidos (escalable)
    EXPENSE_CATEGORIES = {
        "Mantenimiento": [
            "Jardinería",
            "Limpieza",
            "Pintura",
            "Plomería",
            "Electricidad",
            "Carpintería",
            "Otros"
        ],
        "Reparaciones": [
            "Techo",
            "Paredes",
            "Pisos",
            "Baños",
            "Cocina",
            "Ventanas",
            "Puertas",
            "Otros"
        ],
        "Servicios públicos": [
            "Energía eléctrica",
            "Agua/Acueducto",
            "Gas domiciliario",
            "Aseo/Residuos",
            "Internet",
            "Telefonía",
            "Otros"
        ],
        "Seguridad": [
            "Vigilancia",
            "Alarmas",
            "Cámaras",
            "Cerraduras",
            "Otros"
        ],
        "Administración": [
            "Honorarios",
            "Contabilidad",
            "Legal",
            "Papelería y suministros",
            "Otros"
        ],
        "Impuestos y tasas": [
            "Predial",
            "Administrativos",
            "Otros"
        ],
        "Otros": [
            "Varios"
        ]
    }
    
    def __init__(self, parent, on_back: Optional[Callable] = None, expense: Optional[Dict[str, Any]] = None, compact: bool = False, on_navigate_to_dashboard: Optional[Callable] = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.expense_service = ExpenseService()
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard  # Callback para navegar al dashboard
        self.expense = expense  # Si se proporciona, es modo edición
        self.selected_document_path = None
        self.compact_mode = compact  # Modo compacto para edición
        
        # Recargar apartamentos
        apartment_service._load_data()
        self.apartments = apartment_service.get_all_apartments()
        
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal del formulario"""
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header (solo en modo no compacto, o más pequeño en compacto)
        if not self.compact_mode:
            header = tk.Frame(self, bg=cb)
            header.pack(fill="x", pady=(0, Spacing.MD))
            
            # Título a la izquierda
            title_text = "Editar Gasto" if self.expense else "Registrar Nuevo Gasto"
            title = tk.Label(
                header,
                text=title_text,
                font=("Segoe UI", 16, "bold"),
                bg=cb,
                fg=theme["text_primary"]
            )
            title.pack(side="left", padx=(0, Spacing.LG))
            
            # Frame para botones de navegación (alineados a la derecha)
            buttons_frame = tk.Frame(header, bg=cb)
            buttons_frame.pack(side="right")
            
            # Agregar botones Volver y Dashboard
            self._create_navigation_buttons(buttons_frame, self._on_back)
        
        # Contenedor principal (sin scroll) - sin fondo blanco
        main_container = tk.Frame(self, bg=cb)
        container_padx = 4 if self.compact_mode else Spacing.LG
        container_pady = (0, 2) if self.compact_mode else (0, Spacing.MD)
        main_container.pack(fill="both", expand=True, padx=container_padx, pady=container_pady)
        
        # Formulario con mismo fondo que contenido
        form_card = tk.Frame(main_container, bg=cb)
        card_padx = 4 if self.compact_mode else Spacing.MD
        card_pady = 1 if self.compact_mode else Spacing.SM
        form_card.pack(fill="both", expand=True, padx=card_padx, pady=card_pady)
        
        self._build_expense_form(form_card)
    
    def _build_expense_form(self, parent):
        """Construye el formulario de gasto"""
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        # Variables del formulario
        if self.expense and self.expense.get('fecha'):
            try:
                fecha_obj = datetime.strptime(self.expense.get('fecha'), "%Y-%m-%d")
                fecha_str = fecha_obj.strftime("%d/%m/%Y")
            except:
                fecha_str = datetime.now().strftime("%d/%m/%Y")
        else:
            fecha_str = datetime.now().strftime("%d/%m/%Y")
        
        self.fecha_var = tk.StringVar(value=fecha_str)
        self.categoria_var = tk.StringVar(
            value=self.expense.get('categoria', '') if self.expense else ''
        )
        self.subtipo_var = tk.StringVar(
            value=self.expense.get('subtipo', '') if self.expense else ''
        )
        self.apartamento_var = tk.StringVar(
            value=self.expense.get('apartamento', '---') if self.expense else '---'
        )
        self.monto_var = tk.StringVar(
            value=str(self.expense.get('monto', '')) if self.expense else ''
        )
        self.descripcion_var = tk.StringVar(
            value=self.expense.get('descripcion', '') if self.expense else ''
        )
        
        existing_document = self.expense.get('documento') if self.expense else None
        self.selected_document_path = existing_document if existing_document else None
        
        form_container = tk.Frame(parent, bg=cb)
        container_padx = 2 if self.compact_mode else Spacing.MD
        container_pady = 2 if self.compact_mode else Spacing.MD
        if self.compact_mode:
            form_container.pack(fill="both", expand=True, padx=container_padx, pady=container_pady)
        else:
            form_container.pack(fill="x", padx=container_padx, pady=container_pady)
        
        label_width = 20 if self.compact_mode else 25
        row_pady = 1 if self.compact_mode else 4
        
        section_font = ("Segoe UI", 12, "bold") if self.compact_mode else ("Segoe UI", 14, "bold")
        section_title = tk.Label(
            form_container,
            text="Información del Gasto",
            font=section_font,
            bg=cb,
            fg=theme["text_primary"]
        )
        title_pady = (0, 1) if self.compact_mode else (0, Spacing.SM)
        section_title.pack(anchor="w", pady=title_pady)
        
        row1 = tk.Frame(form_container, bg=cb)
        row1.pack(fill="x", pady=row_pady)
        
        tk.Label(row1, text="Fecha del gasto:", width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        # Crear el DatePickerWidget
        self.date_picker = DatePickerWidget(row1)
        self.date_picker.pack(side="left", fill="x", expand=True)
        
        # Sincronizar con fecha_var
        initial_date = self.fecha_var.get()
        if initial_date:
            self.date_picker.set(initial_date)
        
        # Vincular cambios del date_picker a fecha_var
        def on_date_change(event=None):
            fecha_val = self.date_picker.get()
            if fecha_val:
                self.fecha_var.set(fecha_val)
        
        self.date_picker.date_entry.bind("<KeyRelease>", on_date_change)
        self.date_picker.date_entry.bind("<FocusOut>", on_date_change)
        
        # También actualizar cuando se selecciona desde el calendario
        original_select = self.date_picker._select_date
        original_today = self.date_picker._select_today
        
        def wrapped_select_date(day):
            original_select(day)
            self.fecha_var.set(self.date_picker.get())
        
        def wrapped_select_today():
            original_today()
            self.fecha_var.set(self.date_picker.get())
        
        self.date_picker._select_date = wrapped_select_date
        self.date_picker._select_today = wrapped_select_today
        
        # Orden: Apartamento, Categoría, Subtipo
        row2 = tk.Frame(form_container, bg=cb)
        row2.pack(fill="x", pady=row_pady)
        
        tk.Label(row2, text="Apartamento:", width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        apartment_options = ["--- (General)"] + [apt.get('number', 'N/A') for apt in self.apartments]
        apartamento_combo = ttk.Combobox(
            row2,
            textvariable=self.apartamento_var,
            values=apartment_options,
            width=30,
            state="readonly"
        )
        apartamento_combo.pack(side="left", padx=(0, Spacing.SM))
        
        row3 = tk.Frame(form_container, bg=cb)
        row3.pack(fill="x", pady=row_pady)
        
        tk.Label(row3, text="Categoría:", width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        categoria_combo = ttk.Combobox(
            row3,
            textvariable=self.categoria_var,
            values=list(self.EXPENSE_CATEGORIES.keys()),
            width=30,
            state="readonly"
        )
        categoria_combo.pack(side="left", padx=(0, Spacing.SM))
        categoria_combo.bind("<<ComboboxSelected>>", self._on_categoria_changed)
        
        row4 = tk.Frame(form_container, bg=cb)
        row4.pack(fill="x", pady=row_pady)
        
        tk.Label(row4, text="Subtipo:", width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        self.subtipo_combo = ttk.Combobox(
            row4,
            textvariable=self.subtipo_var,
            width=30,
            state="readonly"
        )
        self.subtipo_combo.pack(side="left", padx=(0, Spacing.SM))
        
        # Inicializar subtipos si hay categoría seleccionada
        if self.categoria_var.get():
            self._update_subtipos()
        
        # Fila 5: Monto
        row5 = self._create_form_row(
            form_container,
            "Monto ($):",
            self.monto_var,
            width=29
        )
        
        row6 = tk.Frame(form_container, bg=cb)
        row6.pack(fill="x", pady=row_pady)
        
        tk.Label(row6, text="Descripción:", width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM), anchor="n", pady=(1, 0) if self.compact_mode else (2, 0))
        
        desc_frame = tk.Frame(row6, bg=cb)
        desc_frame.pack(side="left", fill="x", expand=True)
        
        desc_height = 1 if self.compact_mode else 2
        desc_entry = tk.Text(
            desc_frame,
            height=desc_height,
            width=40,
            wrap="word",
            font=("Segoe UI", 10)
        )
        desc_entry.pack(fill="x", expand=True)
        desc_entry.insert("1.0", self.descripcion_var.get())
        self.descripcion_text = desc_entry
        
        row7 = tk.Frame(form_container, bg=cb)
        row7.pack(fill="x", pady=row_pady)
        
        tk.Label(row7, text="Documento adjunto:", width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        doc_frame = tk.Frame(row7, bg=cb)
        doc_frame.pack(side="left", fill="x", expand=True)
        
        self.doc_label = tk.Label(
            doc_frame,
            text="Ningún archivo seleccionado" if not self.selected_document_path else os.path.basename(self.selected_document_path),
            font=("Segoe UI", 9),
            fg=theme.get("text_secondary", "#666") if not self.selected_document_path else "#1976d2",
            anchor="w",
            bg=cb
        )
        self.doc_label.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        btn_select_doc = tk.Button(
            doc_frame,
            text="Seleccionar archivo",
            font=("Segoe UI", 9),
            command=self._select_document,
            cursor="hand2"
        )
        btn_select_doc.pack(side="left", padx=(0, Spacing.SM))
        
        if self.selected_document_path:
            btn_remove_doc = tk.Button(
                doc_frame,
                text="Eliminar",
                font=("Segoe UI", 9),
                fg="#d32f2f",
                command=self._remove_document,
                cursor="hand2"
            )
            btn_remove_doc.pack(side="left")
        
        buttons_frame = tk.Frame(form_container, bg=cb)
        buttons_pady = (4, 2) if self.compact_mode else (Spacing.MD, 0)
        buttons_frame.pack(fill="x", pady=buttons_pady)
        
        button_text = "Actualizar Gasto" if self.expense else "Guardar Gasto"
        btn_save = ModernButton(
            buttons_frame,
            text=button_text,
            icon=Icons.SAVE,
            style="danger",
            command=self._save_expense,
            small=self.compact_mode
        )
        btn_save.pack(side="left", padx=(0, Spacing.SM))

        btn_clear = ModernButton(
            buttons_frame,
            text="Cancelar" if self.expense else "Limpiar",
            icon=Icons.CANCEL,
            style="secondary",
            command=self._clear_form if not self.expense else self._on_back,
            fg="#000000",
            small=self.compact_mode
        )
        btn_clear.pack(side="left")
    
    def _create_form_row(self, parent, label_text, variable, width=20):
        """Crea una fila del formulario con label y entry"""
        cb = self._content_bg
        theme = theme_manager.themes[theme_manager.current_theme]
        row = tk.Frame(parent, bg=cb)
        row_pady = 1 if self.compact_mode else 4
        row.pack(fill="x", pady=row_pady)
        
        label_width = 20 if self.compact_mode else 25
        tk.Label(row, text=label_text, width=label_width, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        entry = tk.Entry(
            row,
            textvariable=variable,
            width=width,
            font=("Segoe UI", 10)
        )
        entry.pack(side="left", padx=(0, Spacing.SM))
        
        return row
    
    def _on_categoria_changed(self, event=None):
        """Actualiza los subtipos cuando cambia la categoría"""
        self._update_subtipos()
        self.subtipo_var.set('')  # Limpiar subtipo seleccionado
    
    def _update_subtipos(self):
        """Actualiza la lista de subtipos según la categoría seleccionada"""
        categoria = self.categoria_var.get()
        if categoria and categoria in self.EXPENSE_CATEGORIES:
            subtipos = self.EXPENSE_CATEGORIES[categoria]
            self.subtipo_combo['values'] = subtipos
        else:
            self.subtipo_combo['values'] = []
    
    def _select_document(self):
        """Permite seleccionar un documento para adjuntar"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar documento",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("PDF", "*.pdf"),
                ("Imágenes", "*.png *.jpg *.jpeg"),
                ("Documentos", "*.doc *.docx *.xls *.xlsx")
            ]
        )
        
        if file_path:
            self.selected_document_path = file_path
            self.doc_label.config(
                text=os.path.basename(file_path),
                fg="#1976d2"
            )
            # Actualizar botón para permitir eliminar
            for widget in self.doc_label.master.winfo_children():
                if isinstance(widget, tk.Button) and widget.cget("text") == "Eliminar":
                    widget.destroy()
            
            btn_remove_doc = tk.Button(
                self.doc_label.master,
                text="Eliminar",
                font=("Segoe UI", 9),
                fg="#d32f2f",
                command=self._remove_document,
                cursor="hand2"
            )
            btn_remove_doc.pack(side="left")
    
    def _remove_document(self):
        """Elimina el documento seleccionado"""
        self.selected_document_path = None
        self.doc_label.config(
            text="Ningún archivo seleccionado",
            fg="#666"
        )
        # Eliminar botón de eliminar
        for widget in self.doc_label.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Eliminar":
                widget.destroy()
    
    def _clear_form(self):
        """Limpia todos los campos del formulario"""
        today_str = datetime.now().strftime("%d/%m/%Y")
        self.fecha_var.set(today_str)
        if hasattr(self, 'date_picker'):
            self.date_picker.set(today_str)
        self.categoria_var.set('')
        self.subtipo_var.set('')
        self.apartamento_var.set('--- (General)')
        self.monto_var.set('')
        self.descripcion_text.delete("1.0", tk.END)
        self._remove_document()
    
    def _save_expense(self):
        """Guarda el gasto"""
        # Obtener fecha del date_picker si está disponible
        fecha_str = self.date_picker.get() if hasattr(self, 'date_picker') else self.fecha_var.get()
        
        # Validaciones
        if not fecha_str:
            messagebox.showerror("Error", "Debe ingresar la fecha del gasto.")
            return
        
        try:
            # Validar formato de fecha
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
            fecha_formatted = fecha_obj.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "La fecha debe tener formato DD/MM/YYYY.")
            return
        
        if not self.categoria_var.get():
            messagebox.showerror("Error", "Debe seleccionar una categoría.")
            return
        
        if not self.subtipo_var.get():
            messagebox.showerror("Error", "Debe seleccionar un subtipo.")
            return
        
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return
        
        # Procesar apartamento
        apartamento = self.apartamento_var.get()
        if apartamento == "--- (General)":
            apartamento = "---"
        
        # Obtener descripción
        descripcion = self.descripcion_text.get("1.0", tk.END).strip()
        
        # Procesar documento
        documento_path = None
        if self.selected_document_path:
            # Si es un archivo nuevo (no es el existente), copiarlo a la carpeta de documentos
            if not self.expense or self.selected_document_path != self.expense.get('documento'):
                documento_path = self._save_document()
            else:
                documento_path = self.selected_document_path
        
        # Preparar datos
        expense_data = {
            "fecha": fecha_formatted,
            "categoria": self.categoria_var.get(),
            "subtipo": self.subtipo_var.get(),
            "apartamento": apartamento,
            "monto": monto,
            "descripcion": descripcion,
            "documento": documento_path
        }
        
        try:
            if self.expense:
                # Modo edición
                updated_expense = self.expense_service.update_expense(self.expense.get('id'), expense_data)
                if updated_expense:
                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    except Exception:
                        pass
                    if self.on_back:
                        self.after(100, self.on_back)
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el gasto.")
            else:
                # Modo creación: solo sonido de confirmación (sin ventana de éxito)
                self.expense_service.add_expense(expense_data)
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
                self._clear_form()
                if self.on_back:
                    self.after(100, self.on_back)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el gasto: {str(e)}")
    
    def _save_document(self):
        """Guarda el documento en la carpeta de gastos"""
        if not self.selected_document_path:
            return None
        
        try:
            # Crear carpeta de documentos si no existe
            from manager.app.paths_config import GASTOS_DOCS_DIR, ensure_dirs
            ensure_dirs()
            docs_folder = GASTOS_DOCS_DIR
            
            # Generar nombre único para el archivo
            original_name = os.path.basename(self.selected_document_path)
            name, ext = os.path.splitext(original_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"gasto_{timestamp}_{name}{ext}"
            
            destination = docs_folder / new_filename
            
            # Copiar archivo
            shutil.copy2(self.selected_document_path, destination)
            
            return str(destination)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el documento: {str(e)}")
            return None
    
    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo consistente"""
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
        
        # Colores rojos para módulo de gastos
        colors = get_module_colors("gastos")
        red_primary = colors["primary"]
        red_hover = colors["hover"]
        red_light = colors["light"]
        red_text = colors["text"]
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard principal)
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if self.on_navigate_to_dashboard:
                try:
                    self.on_navigate_to_dashboard()
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar MainWindow en la jerarquía
            widget = self.master
            max_depth = 10
            depth = 0
            while widget and depth < max_depth:
                if (hasattr(widget, '_navigate_to') and 
                    hasattr(widget, '_load_view') and 
                    hasattr(widget, 'views_container')):
                    try:
                        widget._navigate_to("dashboard")
                        return
                    except Exception as e:
                        print(f"Error al navegar: {e}")
                        break
                widget = getattr(widget, 'master', None)
                depth += 1
            
            # Prioridad 3: Si on_back navega al dashboard principal (desde main_window)
            if self.on_back:
                self.on_back()
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=red_primary,
            hover_bg=red_light,
            hover_fg=red_text,
            command=on_back_command,
            padx=16,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard"
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=red_primary,
            fg_color="white",
            hover_bg=red_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")

    def _on_back(self):
        """Maneja el botón de volver"""
        if self.on_back:
            self.on_back()
