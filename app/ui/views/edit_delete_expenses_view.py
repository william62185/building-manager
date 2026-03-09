"""
Vista completa para editar y eliminar gastos del edificio
Diseño escalable y profesional
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Optional, Dict, Any, Callable

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors
from manager.app.services.expense_service import ExpenseService
from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import TenantService

# Importar RegisterExpenseView para acceder a EXPENSE_CATEGORIES
from manager.app.ui.views.register_expense_view import RegisterExpenseView

# Placeholder del cuadro de búsqueda (una sola constante para comparar y restaurar)
SEARCH_PLACEHOLDER = "Buscar por nombre de inquilino o número de apartamento..."


class EditDeleteExpensesView(tk.Frame):
    """Vista profesional para editar/eliminar gastos"""
    
    def __init__(self, parent, on_back: Optional[Callable] = None, on_navigate_to_dashboard: Optional[Callable] = None,
                 on_register_new_expense: Optional[Callable] = None, on_show_reports: Optional[Callable] = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.expense_service = ExpenseService()
        self.tenant_service = TenantService()
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.on_register_new_expense = on_register_new_expense
        self.on_show_reports = on_show_reports
        self.editing_expense = None
        self.filter_category = None
        self.filter_apartment = None
        self.filter_year = None
        self.filter_month = None
        self.search_text = ""
        
        apartment_service._load_data()
        self.apartments = apartment_service.get_all_apartments()
        self.tenants = self.tenant_service.get_all_tenants()
        
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal"""
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        for widget in self.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self, bg=cb)
        header.pack(fill="x", pady=(0, Spacing.SM))
        buttons_frame = tk.Frame(header, bg=cb)
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame, self._on_back, show_back_button=False)

        # Cards: Registrar nuevo gasto y Reportes (igual que en Pagos)
        self._create_action_cards(self)

        fixed_container = tk.Frame(self, bg=cb)
        fixed_container.pack(fill="x", padx=Spacing.LG, pady=(0, 4))
        
        search_frame = tk.Frame(fixed_container, bg=cb)
        search_frame.pack(fill="x", pady=(0, 2))
        
        tk.Label(search_frame, text="Búsqueda:", font=("Segoe UI", 11), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_search_change())
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=55,
            font=("Segoe UI", 10),
            bg=cb
        )
        self.search_entry.pack(side="left", padx=(0, Spacing.SM))
        self.search_var.set(SEARCH_PLACEHOLDER)
        self.search_entry.configure(fg="#999")
        
        def _clear_placeholder_and_show_input():
            if self.search_var.get().strip() == SEARCH_PLACEHOLDER:
                self.search_var.set("")
            self.search_entry.configure(fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#000"))
        
        def on_search_focus_in(event):
            if self.search_var.get().strip() == SEARCH_PLACEHOLDER:
                self.search_var.set("")
            self.search_entry.configure(fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#000"))
        
        def on_search_keypress(event):
            # Si el contenido es solo el placeholder, limpiar antes de que se inserte la tecla (evita mezcla)
            if self.search_var.get() == SEARCH_PLACEHOLDER:
                self.search_var.set("")
                self.search_entry.configure(fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#000"))
        
        def on_search_focus_out(event):
            if not self.search_var.get().strip():
                self.search_var.set(SEARCH_PLACEHOLDER)
                self.search_entry.configure(fg="#999")
        
        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)
        self.search_entry.bind("<KeyPress>", on_search_keypress)
        # Posicionar cursor en el cuadro de búsqueda al abrir la vista
        self.after(150, self._focus_search_entry)
        
        filters_frame = tk.Frame(fixed_container, bg=cb)
        filters_frame.pack(fill="x", pady=(0, 4))
        
        tk.Label(filters_frame, text="Filtros:", font=("Segoe UI", 11, "bold"), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        
        tk.Label(filters_frame, text="Categoría:", font=("Segoe UI", 10), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, 4))
        
        self.category_filter_var = tk.StringVar()
        self.category_filter_var.trace("w", lambda *args: self._apply_filters())
        category_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.category_filter_var,
            values=["Todas"] + list(RegisterExpenseView.EXPENSE_CATEGORIES.keys()),
            width=18,
            state="readonly"
        )
        category_combo.set("Todas")
        category_combo.pack(side="left", padx=(0, Spacing.SM))

        tk.Label(filters_frame, text="Apartamento:", font=("Segoe UI", 10), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, 4))
        
        self.apartment_filter_var = tk.StringVar()
        self.apartment_filter_var.trace("w", lambda *args: self._apply_filters())
        apartment_options = ["Todos"] + ["--- (General)"] + [apt.get('number', 'N/A') for apt in self.apartments]
        apartment_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.apartment_filter_var,
            values=apartment_options,
            width=15,
            state="readonly"
        )
        apartment_combo.set("Todos")
        apartment_combo.pack(side="left", padx=(0, Spacing.SM))

        tk.Label(filters_frame, text="Año:", font=("Segoe UI", 10), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, 4))
        
        self.year_filter_var = tk.StringVar()
        self.year_filter_var.trace("w", lambda *args: self._apply_filters())
        current_year = datetime.now().year
        years = ["Todos"] + [str(y) for y in range(current_year - 5, current_year + 2)]
        year_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.year_filter_var,
            values=years,
            width=10,
            state="readonly"
        )
        year_combo.set("Todos")
        year_combo.pack(side="left", padx=(0, Spacing.SM))

        tk.Label(filters_frame, text="Mes:", font=("Segoe UI", 10), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, 4))
        
        self.month_filter_var = tk.StringVar()
        self.month_filter_var.trace("w", lambda *args: self._apply_filters())
        months = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        month_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.month_filter_var,
            values=months,
            width=12,
            state="readonly"
        )
        month_combo.set("Todos")
        month_combo.pack(side="left", padx=(0, Spacing.SM))

        btn_clear_filters = ModernButton(
            filters_frame,
            text="Limpiar filtros",
            icon=Icons.CANCEL,
            style="danger",
            command=self._clear_filters,
            small=True,
            fg="#000000"
        )
        btn_clear_filters.pack(side="left", padx=(Spacing.MD, 0))
        
        self.edit_placeholder = tk.Frame(fixed_container, bg=cb)
        self.edit_placeholder.pack_forget()
        
        separator = tk.Frame(self, height=2, bg=theme.get("border_light", "#e0e0e0"))
        separator.pack(fill="x", padx=Spacing.LG, pady=(0, 4))

        # Listado de gastos (altura limitada para dejar espacio a las cards)
        self._create_expenses_list()

    def _create_action_cards(self, parent):
        """Dos cards del mismo tamaño: Registrar nuevo gasto y Reportes (como en Pagos)."""
        cb = self._content_bg
        colors = get_module_colors("gastos")
        card_bg = colors.get("primary", "#991b1b")
        card_hover = colors.get("hover", "#b91c1c")
        cards_frame = tk.Frame(parent, bg=cb)
        cards_frame.pack(fill="x", padx=Spacing.LG, pady=(0, 8))
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        btn_register = tk.Button(
            cards_frame,
            text=f"{Icons.EXPENSES} Registrar nuevo gasto",
            font=("Segoe UI", 11, "bold"),
            bg=card_bg,
            fg="white",
            relief="flat",
            padx=12,
            pady=10,
            cursor="hand2",
            command=self._on_register_card,
        )
        btn_register.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        btn_register.bind("<Enter>", lambda e: btn_register.config(bg=card_hover))
        btn_register.bind("<Leave>", lambda e: btn_register.config(bg=card_bg))
        btn_reports = tk.Button(
            cards_frame,
            text=f"{Icons.REPORTS} Reportes",
            font=("Segoe UI", 11, "bold"),
            bg="#6b7280",
            fg="white",
            relief="flat",
            padx=12,
            pady=10,
            cursor="hand2",
            command=self._on_reports_card,
        )
        btn_reports.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        btn_reports.bind("<Enter>", lambda e: btn_reports.config(bg="#4b5563"))
        btn_reports.bind("<Leave>", lambda e: btn_reports.config(bg="#6b7280"))

    def _on_register_card(self):
        if self.on_register_new_expense:
            self.on_register_new_expense()

    def _on_reports_card(self):
        if self.on_show_reports:
            self.on_show_reports()

    def _focus_search_entry(self):
        """Coloca el foco en el cuadro de búsqueda al abrir la vista Editar/Eliminar gastos."""
        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.focus_set()
    
    def _on_search_change(self):
        """Maneja cambios en el campo de búsqueda"""
        search_value = self.search_var.get()
        if search_value == SEARCH_PLACEHOLDER or not search_value.strip():
            self.search_text = ""
        else:
            self.search_text = search_value.strip().lower()
        self._create_expenses_list()
    
    def _apply_filters(self):
        """Aplica los filtros seleccionados"""
        # Verificar que las variables existan antes de acceder
        if not hasattr(self, 'category_filter_var'):
            return
        
        # Actualizar filtros
        category = self.category_filter_var.get()
        self.filter_category = None if category == "Todas" else category
        
        if hasattr(self, 'apartment_filter_var'):
            apartment = self.apartment_filter_var.get()
            if apartment == "Todos":
                self.filter_apartment = None
            elif apartment == "--- (General)":
                self.filter_apartment = "---"
            else:
                self.filter_apartment = apartment
        else:
            self.filter_apartment = None
        
        if hasattr(self, 'year_filter_var'):
            year = self.year_filter_var.get()
            self.filter_year = None if year == "Todos" else int(year)
        else:
            self.filter_year = None
        
        if hasattr(self, 'month_filter_var'):
            month = self.month_filter_var.get()
            month_map = {
                "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
                "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
                "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
            }
            self.filter_month = None if month == "Todos" else month_map.get(month)
        else:
            self.filter_month = None
        
        # Recrear la lista con los filtros aplicados
        self._create_expenses_list()
    
    def _clear_filters(self):
        """Limpia todos los filtros y restaura el placeholder de búsqueda sin mezclarlo con texto."""
        self.category_filter_var.set("Todas")
        self.apartment_filter_var.set("Todos")
        self.year_filter_var.set("Todos")
        self.month_filter_var.set("Todos")
        self.search_var.set(SEARCH_PLACEHOLDER)
        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.configure(fg="#999")
        self.filter_category = None
        self.filter_apartment = None
        self.filter_year = None
        self.filter_month = None
        self.search_text = ""
        
        self.editing_expense = None
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        self.edit_placeholder.pack_forget()
        
        self._create_expenses_list()
    
    def _create_expenses_list(self):
        """Crea el listado de gastos con scroll"""
        if hasattr(self, 'list_container'):
            self.list_container.destroy()
        
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        bg_alt = theme.get("bg_tertiary", "#f0f4fa")
        header_bg = "#fee2e2"
        header_fg = "#991b1b"
        
        # Altura limitada del listado para liberar espacio arriba (cards + filtros)
        list_height = 320
        self.list_container = tk.Frame(self, bg=cb, height=list_height)
        self.list_container.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        self.list_container.pack_propagate(False)
        
        columns = [
            ("ID", 5),
            ("Fecha", 14),
            ("Categoría", 18),
            ("Subtipo", 18),
            ("Apartamento", 12),
            ("Monto", 14),
            ("Descripción", 32),
            ("Acciones", 12)
        ]
        
        sep_color = theme.get("border_light", "#d1d5db")
        # Un solo grid: encabezado y cuerpo comparten las mismas columnas para alineación exacta
        table_grid = tk.Frame(self.list_container, bg=cb)
        table_grid.pack(fill="both", expand=True)
        for i in range(8):
            table_grid.grid_columnconfigure(i, weight=1)
        table_grid.grid_columnconfigure(8, weight=0, minsize=17)
        # Fila 0: encabezado (columnas 0-7)
        header_frame = tk.Frame(table_grid, bg=header_bg)
        header_frame.grid(row=0, column=0, columnspan=8, sticky="nsew")
        for idx in range(8):
            header_frame.grid_columnconfigure(idx, weight=1)
        col_anchors = ["w", "w", "w", "w", "w", "w", "w", "c"]  # Monto a la izquierda como el resto
        for idx, (col, width) in enumerate(columns):
            anc = col_anchors[idx] if idx < len(col_anchors) else "w"
            tk.Label(header_frame, text=col, font=("Segoe UI", 10, "bold"), width=width, anchor=anc, bg=header_bg, fg=header_fg).grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
        scrollbar_header_placeholder = tk.Frame(table_grid, width=17, bg=header_bg)
        scrollbar_header_placeholder.grid(row=0, column=8, sticky="ns")
        scrollbar_header_placeholder.pack_propagate(False)
        # Fila 1: línea separadora
        header_sep = tk.Frame(table_grid, height=2, bg=sep_color)
        header_sep.grid(row=1, column=0, columnspan=8, sticky="ew")
        header_sep.grid_propagate(False)
        tk.Frame(table_grid, width=17, bg=cb).grid(row=1, column=8)
        # Fila 2: canvas (columnas 0-7) + scrollbar (columna 8)
        table_grid.grid_rowconfigure(2, weight=1)
        canvas_holder = tk.Frame(table_grid, bg=cb)
        canvas_holder.grid(row=2, column=0, columnspan=8, sticky="nsew")
        canvas = tk.Canvas(canvas_holder, bg=cb, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(table_grid, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=2, column=8, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        content_frame = tk.Frame(canvas, bg=cb)
        list_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", _on_frame_configure)
        
        def _on_canvas_configure(event):
            if event.width > 0:
                canvas.itemconfig(list_window, width=event.width)
        
        canvas.bind("<Configure>", _on_canvas_configure)
        
        # Scroll con mouse (comprobar que el canvas siga existiendo: la lista puede recrearse)
        def _on_mousewheel(event):
            if not canvas.winfo_exists():
                return
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            try:
                canvas.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        content_frame.bind('<Enter>', _bind_mousewheel)
        content_frame.bind('<Leave>', _unbind_mousewheel)
        
        # Obtener gastos filtrados
        expenses = self.expense_service.get_all_expenses()
        
        # Aplicar búsqueda inteligente (por nombre de inquilino o número de apartamento)
        if self.search_text:
            # Buscar apartamentos relacionados con inquilinos que coincidan
            matching_apartments = set()
            
            # Buscar por número de apartamento directamente
            for apt in self.apartments:
                apt_number = str(apt.get('number', '')).lower()
                if self.search_text in apt_number:
                    matching_apartments.add(apt_number)
                    matching_apartments.add(str(apt.get('number', '')))  # También el número original
            
            # Buscar por nombre de inquilino
            for tenant in self.tenants:
                tenant_name = str(tenant.get('nombre', '')).lower()
                if self.search_text in tenant_name:
                    # Obtener el apartamento del inquilino
                    apt_id = tenant.get('apartamento')
                    if apt_id is not None:
                        try:
                            apt = apartment_service.get_apartment_by_id(int(apt_id))
                            if apt and 'number' in apt:
                                apt_number = str(apt.get('number', ''))
                                matching_apartments.add(apt_number)
                                matching_apartments.add(apt_number.lower())
                        except:
                            pass
            
            # Filtrar gastos que coincidan con la búsqueda
            filtered_expenses = []
            for e in expenses:
                expense_apt = str(e.get("apartamento", "")).lower()
                expense_apt_original = str(e.get("apartamento", ""))
                
                # Verificar si el apartamento del gasto coincide
                if (expense_apt in matching_apartments or 
                    expense_apt_original in matching_apartments or
                    self.search_text in expense_apt or
                    self.search_text in expense_apt_original):
                    filtered_expenses.append(e)
            
            expenses = filtered_expenses
        
        # Aplicar filtros
        if self.filter_category:
            expenses = [e for e in expenses if e.get("categoria") == self.filter_category]
        
        if self.filter_apartment:
            expenses = [e for e in expenses if str(e.get("apartamento", "")) == str(self.filter_apartment)]
        
        if self.filter_year is not None or self.filter_month is not None:
            filtered = []
            for e in expenses:
                fecha_str = e.get("fecha", "")
                if fecha_str:
                    try:
                        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                        if self.filter_year is not None and fecha.year != self.filter_year:
                            continue
                        if self.filter_month is not None and fecha.month != self.filter_month:
                            continue
                        filtered.append(e)
                    except:
                        continue
            expenses = filtered
        
        # Ordenar por fecha (más recientes primero)
        expenses.sort(key=lambda x: x.get("fecha", ""), reverse=True)
        
        zebra_colors = (cb, bg_alt)
        
        if not expenses:
            no_data_frame = tk.Frame(content_frame, bg=cb)
            no_data_frame.grid(row=0, column=0, columnspan=8, sticky="ew", pady=20)
            tk.Label(
                no_data_frame,
                text="No se encontraron gastos con los filtros seleccionados.",
                font=("Segoe UI", 11),
                fg=theme.get("text_secondary", "#666"),
                bg=cb
            ).pack()
            content_frame.grid_columnconfigure(0, weight=1)
        else:
            for row_idx, expense in enumerate(expenses):
                bg_color = zebra_colors[row_idx % 2]
                row = tk.Frame(content_frame, bg=bg_color)
                row.grid(row=row_idx, column=0, columnspan=8, sticky="ew")
                
                # Formatear fecha
                fecha_str = expense.get("fecha", "")
                fecha_display = ""
                if fecha_str:
                    try:
                        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                        fecha_display = fecha_obj.strftime("%d/%m/%Y")
                    except:
                        fecha_display = fecha_str
                
                # Formatear apartamento
                apt = expense.get("apartamento", "---")
                apt_display = "General" if apt == "---" else apt
                
                # Formatear descripción (truncar si es muy larga)
                desc = expense.get("descripcion", "")
                desc_display = desc[:50] + "..." if len(desc) > 50 else desc
                
                values = [
                    str(expense.get("id", "")),
                    fecha_display,
                    expense.get("categoria", ""),
                    expense.get("subtipo", ""),
                    apt_display,
                    f"${expense.get('monto', 0):,.2f}",
                    desc_display
                ]
                
                # Configurar columnas del row para que coincidan con el encabezado
                for idx in range(len(columns)):
                    row.grid_columnconfigure(idx, weight=1)
                
                # Monto (col 5) alineado a la derecha; el resto a la izquierda
                data_anchors = ["w", "w", "w", "w", "w", "w", "w"]  # Todas a la izquierda, incluido Monto
                for col_idx, (val, (_, width)) in enumerate(zip(values, columns)):
                    anc = data_anchors[col_idx] if col_idx < len(data_anchors) else "w"
                    tk.Label(
                        row,
                        text=val,
                        font=("Segoe UI", 10),
                        width=width,
                        anchor=anc,
                        bg=bg_color,
                        fg=theme["text_primary"]
                    ).grid(row=0, column=col_idx, padx=(0, 1), sticky="nsew")
                
                # Acciones: botones editar y eliminar
                actions_frame = tk.Frame(row, bg=bg_color)
                actions_frame.grid(row=0, column=len(values), padx=(0, 1), sticky="nsew")
                
                btn_edit = tk.Button(
                    actions_frame,
                    text=Icons.EDIT,
                    font=("Segoe UI", 12),
                    fg="#1976d2",
                    bg=bg_color,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    command=lambda e=expense: self._show_edit_form(e)
                )
                btn_edit.pack(side="left", padx=(0, 6))
                
                btn_delete = tk.Button(
                    actions_frame,
                    text=Icons.DELETE,
                    font=("Segoe UI", 12),
                    fg="#d32f2f",
                    bg=bg_color,
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    command=lambda e=expense: self._delete_expense(e)
                )
                btn_delete.pack(side="left")
                
                row.grid_columnconfigure(len(values), weight=1)
        
        # Mismo weight en todas las columnas para que header y filas compartan anchos (como en listado de pagos)
        for idx in range(len(columns)):
            content_frame.grid_columnconfigure(idx, weight=1)
    
    def _show_edit_form(self, expense: Dict[str, Any]):
        """Muestra el formulario de edición para un gasto"""
        self.editing_expense = expense
        
        # Filtrar el listado por el mismo apartamento del gasto que estamos editando
        apt = expense.get("apartamento", "---")
        if apt == "---" or apt is None:
            self.apartment_filter_var.set("--- (General)")
            self.filter_apartment = "---"
        else:
            self.apartment_filter_var.set(str(apt))
            self.filter_apartment = str(apt)
        
        # Limpiar contenido anterior
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        
        # Mostrar el contenedor de edición dentro de fixed_container
        if not self.edit_placeholder.winfo_ismapped():
            self.edit_placeholder.pack(
                fill="both",
                expand=True,
                pady=(0, 4)
            )
        
        # Crear el formulario de edición directamente (sin scroll, más compacto)
        # Usar un callback personalizado que actualice la lista
        def on_expense_saved():
            # Recargar los datos del servicio antes de actualizar la lista
            self.expense_service._load_data()
            self._cancel_edit()
            self._create_expenses_list()  # Actualizar la lista automáticamente
        
        edit_form = RegisterExpenseView(
            self.edit_placeholder,
            on_back=on_expense_saved,
            expense=expense,
            compact=True  # Modo compacto para edición
        )
        # Empaquetar el formulario para que sea visible completamente
        edit_form.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Refrescar el listado para mostrar solo gastos del mismo apartamento
        self._create_expenses_list()
        self.edit_placeholder.update_idletasks()
    
    def _cancel_edit(self):
        """Cancela la edición, limpia filtros y búsqueda, y vuelve al listado completo (para nueva búsqueda sin limpiar a mano)."""
        self._clear_filters()
    
    def _delete_expense(self, expense: Dict[str, Any]):
        """Elimina un gasto"""
        # Confirmar eliminación
        fecha_str = expense.get("fecha", "")
        categoria = expense.get("categoria", "")
        monto = expense.get("monto", 0)
        
        try:
            if fecha_str:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                fecha_display = fecha_obj.strftime("%d/%m/%Y")
            else:
                fecha_display = fecha_str
        except:
            fecha_display = fecha_str
        
        confirm_msg = (
            f"¿Seguro que deseas eliminar este gasto?\n\n"
            f"Fecha: {fecha_display}\n"
            f"Categoría: {categoria}\n"
            f"Monto: ${monto:,.2f}"
        )
        
        if messagebox.askyesno("Eliminar gasto", confirm_msg):
            success = self.expense_service.delete_expense(expense.get('id'))
            
            if success:
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
                # Si estaba editando este gasto, cancelar la edición
                if self.editing_expense and self.editing_expense.get('id') == expense.get('id'):
                    self._cancel_edit()
                else:
                    self._create_expenses_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el gasto.")
    
    def _create_navigation_buttons(self, parent, on_back_command, show_back_button=False):
        """Crea el botón Dashboard y opcionalmente Volver (en esta vista solo Dashboard, como en Pagos)."""
        theme = theme_manager.themes[theme_manager.current_theme]
        colors = get_module_colors("gastos")
        red_primary = colors["primary"]
        red_hover = colors["hover"]
        red_light = colors["light"]
        red_text = colors["text"]

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

        if show_back_button:
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
