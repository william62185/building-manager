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
from manager.app.logger import logger

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
        self._updating_filters = False

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
        
        fixed_container = tk.Frame(self, bg=cb)
        fixed_container.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, 4))
        
        search_frame = tk.Frame(fixed_container, bg=cb)
        search_frame.pack(fill="x", pady=(0, 2))
        
        tk.Label(search_frame, text="Búsqueda:", font=("Segoe UI", 11), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))

        border_color = theme.get("border_light", "#e5e7eb")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_search_change())
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=55,
            font=("Segoe UI", 12),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=border_color,
            highlightcolor=border_color,
            bg=theme.get("bg_primary", "#ffffff"),
            fg="#6b7280",
            insertbackground=theme.get("text_primary", "#1f2937"),
        )
        self.search_entry.pack(side="left", pady=(4, 4), padx=(0, Spacing.SM))
        self.search_var.set(SEARCH_PLACEHOLDER)

        def on_search_focus_in(event):
            if self.search_var.get() == SEARCH_PLACEHOLDER:
                self.search_var.set("")
            self.search_entry.configure(fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#000"))

        def on_search_keypress(event):
            if self.search_var.get() == SEARCH_PLACEHOLDER:
                self.search_var.set("")
                self.search_entry.configure(fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#000"))

        def on_search_focus_out(event):
            if not self.search_var.get().strip():
                self.search_var.set(SEARCH_PLACEHOLDER)
                self.search_entry.configure(fg="#6b7280")

        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)
        self.search_entry.bind("<KeyPress>", on_search_keypress)

        # Dar foco al search entry al abrir la vista (se registra después del after del Treeview, así gana)
        self.after(150, self._focus_search_entry)
        
        from manager.app.ui.components.modern_widgets import bind_combobox_dropdown_on_click

        filters_frame = tk.Frame(fixed_container, bg=cb)
        filters_frame.pack(fill="x", pady=(0, 4))

        tk.Label(filters_frame, text="Filtros:", font=("Segoe UI", 11, "bold"), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))

        tk.Label(filters_frame, text="Categoría:", font=("Segoe UI", 10), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, 4))

        self._updating_filters = True
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
        bind_combobox_dropdown_on_click(category_combo)

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
        bind_combobox_dropdown_on_click(apartment_combo)

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
        bind_combobox_dropdown_on_click(year_combo)

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
        bind_combobox_dropdown_on_click(month_combo)
        self._updating_filters = False  # habilitar traces ahora que todos los combos están inicializados

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

        # Listado de gastos
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
        if self._updating_filters:
            return
        search_value = self.search_var.get()
        if search_value == SEARCH_PLACEHOLDER or not search_value.strip():
            new_search_text = ""
        else:
            new_search_text = search_value.strip().lower()
        # Evita reconstruir la tabla cuando el valor lógico de búsqueda no cambió
        # (p. ej. al restaurar placeholder en FocusOut).
        if new_search_text == self.search_text:
            return
        self.search_text = new_search_text
        self._create_expenses_list()

    def _apply_filters(self):
        """Aplica los filtros seleccionados"""
        if self._updating_filters:
            return
        if not hasattr(self, 'category_filter_var'):
            return

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

        self._create_expenses_list()
    
    def _clear_search(self):
        """Limpia solo el campo de búsqueda y restaura el placeholder."""
        self.search_var.set(SEARCH_PLACEHOLDER)
        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.configure(fg="#6b7280")
        self.search_text = ""
        self._create_expenses_list()

    def _clear_filters(self):
        """Limpia todos los filtros y restaura el placeholder de búsqueda sin mezclarlo con texto."""
        self._updating_filters = True
        self.category_filter_var.set("Todas")
        self.apartment_filter_var.set("Todos")
        self.year_filter_var.set("Todos")
        self.month_filter_var.set("Todos")
        self.search_var.set(SEARCH_PLACEHOLDER)
        self._updating_filters = False

        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.configure(fg="#6b7280")
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
        """Crea el listado de gastos usando Treeview para máximo rendimiento."""
        if hasattr(self, 'list_container'):
            self.list_container.destroy()

        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg

        self.list_container = tk.Frame(self, bg=cb)
        self.list_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.SM))

        # Obtener y filtrar gastos
        expenses = self.expense_service.get_all_expenses()

        if self.search_text:
            # Pre-construir mapa apt_number → set para búsqueda eficiente
            apt_map_search = {str(a.get('number', '')).lower(): str(a.get('number', '')) for a in self.apartments}
            matching_apts = set()
            for apt in self.apartments:
                if self.search_text in str(apt.get('number', '')).lower():
                    matching_apts.add(str(apt.get('number', '')))
            for tenant in self.tenants:
                if self.search_text in str(tenant.get('nombre', '')).lower():
                    apt_id = tenant.get('apartamento')
                    if apt_id is not None:
                        apt_obj = next((a for a in self.apartments if a.get('id') == apt_id), None)
                        if apt_obj:
                            matching_apts.add(str(apt_obj.get('number', '')))
            expenses = [
                e for e in expenses
                if (self.search_text in str(e.get("apartamento", "")).lower()
                    or str(e.get("apartamento", "")) in matching_apts)
            ]

        if self.filter_category:
            expenses = [e for e in expenses if e.get("categoria") == self.filter_category]
        if self.filter_apartment:
            expenses = [e for e in expenses if str(e.get("apartamento", "")) == str(self.filter_apartment)]
        if self.filter_year is not None or self.filter_month is not None:
            filtered = []
            for e in expenses:
                try:
                    fecha = datetime.strptime(e.get("fecha", ""), "%Y-%m-%d")
                    if self.filter_year is not None and fecha.year != self.filter_year:
                        continue
                    if self.filter_month is not None and fecha.month != self.filter_month:
                        continue
                    filtered.append(e)
                except Exception:
                    continue
            expenses = filtered

        expenses.sort(key=lambda x: (x.get("fecha", ""), x.get("id", 0)), reverse=True)

        # Hint prominente encima de la tabla
        hint_frame = tk.Frame(self.list_container, bg=theme.get("bg_tertiary", "#f0f4fa"))
        hint_frame.pack(fill="x", pady=(0, 4))
        tk.Label(
            hint_frame,
            text="  ✎ Doble clic para editar   ✕ Supr para eliminar",
            font=("Segoe UI", 9),
            bg=theme.get("bg_tertiary", "#f0f4fa"),
            fg=theme.get("text_secondary", "#6b7280"),
            anchor="w",
            pady=4,
        ).pack(fill="x", padx=6)

        # Treeview
        columns = ("fecha", "categoria", "subtipo", "apartamento", "monto", "descripcion")
        self._exp_tree = ttk.Treeview(
            self.list_container, columns=columns,
            show="headings", selectmode="browse",
        )
        col_cfg = [
            ("fecha",       "Fecha",        90),
            ("categoria",   "Categoría",   130),
            ("subtipo",     "Subtipo",      130),
            ("apartamento", "Apartamento",  100),
            ("monto",       "Monto",         90),
            ("descripcion", "Descripción",  280),
        ]
        for col_id, heading, width in col_cfg:
            self._exp_tree.heading(col_id, text=heading)
            self._exp_tree.column(col_id, width=width, minwidth=50, anchor="w")

        self._exp_tree.tag_configure("odd",  background=cb)
        self._exp_tree.tag_configure("even", background=theme.get("bg_tertiary", "#f0f4fa"))

        scrollbar = ttk.Scrollbar(self.list_container, orient="vertical", command=self._exp_tree.yview)
        self._exp_tree.configure(yscrollcommand=scrollbar.set)
        self._exp_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._expenses_index = {}
        if not expenses:
            self._exp_tree.insert("", "end", values=(
                "", "No se encontraron gastos.", "", "", "", "",
            ))
        else:
            for idx, expense in enumerate(expenses):
                fecha_str = expense.get("fecha", "")
                try:
                    fecha_display = datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    fecha_display = fecha_str
                apt = expense.get("apartamento", "---")
                apt_display = "General" if apt == "---" else apt
                desc = expense.get("descripcion", "")
                tag = "odd" if idx % 2 == 0 else "even"
                iid = self._exp_tree.insert("", "end", tags=(tag,), values=(
                    fecha_display,
                    expense.get("categoria", ""),
                    expense.get("subtipo", ""),
                    apt_display,
                    f"${expense.get('monto', 0):,.2f}",
                    desc[:80] + "..." if len(desc) > 80 else desc,
                ))
                self._expenses_index[iid] = expense

        self._exp_tree.bind("<Double-1>", self._on_exp_tree_double_click)
        self._exp_tree.bind("<Delete>", self._on_exp_tree_delete_key)

    def _on_exp_tree_double_click(self, event=None):
        row_id = self._exp_tree.identify_row(event.y) if event else ""
        if not row_id:
            sel = self._exp_tree.selection()
            row_id = sel[0] if sel else ""
        if not row_id:
            return
        expense = self._expenses_index.get(row_id)
        if expense:
            self._show_edit_form(expense)

    def _on_exp_tree_delete_key(self, event=None):
        sel = self._exp_tree.selection()
        if not sel:
            return
        expense = self._expenses_index.get(sel[0])
        if expense:
            self._delete_expense(expense)
        
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
            if not self.winfo_exists():
                return
            success = self.expense_service.delete_expense(expense.get('id'))
            
            if success:
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
                # Si estaba editando este gasto, cancelar la edición
                if self.editing_expense and self.editing_expense.get('id') == expense.get('id'):
                    if self.winfo_exists():
                        self._cancel_edit()
                else:
                    if self.winfo_exists():
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
                    logger.warning("Error en callback de navegación: %s", e)
            
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
                        logger.warning("Error al navegar: %s", e)
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
