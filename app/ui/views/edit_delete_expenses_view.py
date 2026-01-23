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
from manager.app.ui.components.modern_widgets import ModernButton
from manager.app.services.expense_service import ExpenseService
from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import TenantService

# Importar RegisterExpenseView para acceder a EXPENSE_CATEGORIES
from manager.app.ui.views.register_expense_view import RegisterExpenseView


class EditDeleteExpensesView(tk.Frame):
    """Vista profesional para editar/eliminar gastos"""
    
    def __init__(self, parent, on_back: Optional[Callable] = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.expense_service = ExpenseService()
        self.tenant_service = TenantService()
        self.on_back = on_back
        self.editing_expense = None
        self.filter_category = None
        self.filter_apartment = None
        self.filter_year = None
        self.filter_month = None
        self.search_text = ""  # Texto de búsqueda
        
        # Recargar apartamentos e inquilinos
        apartment_service._load_data()
        self.apartments = apartment_service.get_all_apartments()
        self.tenants = self.tenant_service.get_all_tenants()
        
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG))
        
        btn_back = ModernButton(
            header,
            text="Volver",
            icon=Icons.ARROW_LEFT,
            style="secondary",
            command=self._on_back
        )
        btn_back.pack(side="left")
        
        title = tk.Label(
            header,
            text="Editar/Eliminar Gastos",
            **theme_manager.get_style("label_title")
        )
        title.pack(side="left", padx=(Spacing.LG, 0))
        
        # Contenedor fijo para filtros y búsqueda (no se mueve con scroll)
        fixed_container = tk.Frame(self, **theme_manager.get_style("frame"))
        fixed_container.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        
        # Búsqueda inteligente
        search_frame = tk.Frame(fixed_container, **theme_manager.get_style("frame"))
        search_frame.pack(fill="x", pady=(0, Spacing.SM))
        
        tk.Label(
            search_frame,
            text="Búsqueda:",
            **theme_manager.get_style("label_body")
        ).pack(side="left", padx=(0, Spacing.SM))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_search_change())
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40,
            font=("Segoe UI", 10)
        )
        search_entry.pack(side="left", padx=(0, Spacing.SM))
        search_entry.insert(0, "Buscar por nombre de inquilino o número de apartamento...")
        search_entry.configure(fg="#999")
        
        def on_search_focus_in(event):
            current_text = search_entry.get()
            if current_text == "Buscar por nombre de inquilino o número de apartamento...":
                search_entry.delete(0, tk.END)
                search_entry.configure(fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#000"))
        
        def on_search_focus_out(event):
            if not search_entry.get().strip():
                search_entry.delete(0, tk.END)
                search_entry.insert(0, "Buscar por nombre de inquilino o número de apartamento...")
                search_entry.configure(fg="#999")
        
        search_entry.bind("<FocusIn>", on_search_focus_in)
        search_entry.bind("<FocusOut>", on_search_focus_out)
        
        # Filtros
        filters_frame = tk.Frame(fixed_container, **theme_manager.get_style("frame"))
        filters_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        # Título de filtros
        filters_style = theme_manager.get_style("label_body").copy()
        filters_style["font"] = ("Segoe UI", 11, "bold")
        filters_title = tk.Label(
            filters_frame,
            text="Filtros:",
            **filters_style
        )
        filters_title.pack(side="left", padx=(0, Spacing.SM))
        
        # Filtro por categoría
        tk.Label(
            filters_frame,
            text="Categoría:",
            **theme_manager.get_style("label_body")
        ).pack(side="left", padx=(0, 4))
        
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
        
        # Filtro por apartamento
        tk.Label(
            filters_frame,
            text="Apartamento:",
            **theme_manager.get_style("label_body")
        ).pack(side="left", padx=(0, 4))
        
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
        
        # Filtro por año
        tk.Label(
            filters_frame,
            text="Año:",
            **theme_manager.get_style("label_body")
        ).pack(side="left", padx=(0, 4))
        
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
        
        # Filtro por mes
        tk.Label(
            filters_frame,
            text="Mes:",
            **theme_manager.get_style("label_body")
        ).pack(side="left", padx=(0, 4))
        
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
        
        # Botón limpiar filtros
        btn_clear_filters = ModernButton(
            filters_frame,
            text="Limpiar filtros",
            icon=Icons.CANCEL,
            style="warning",
            command=self._clear_filters,
            small=True
        )
        btn_clear_filters.pack(side="left", padx=(Spacing.MD, 0))
        
        # Contenedor para el formulario de edición (dentro del área fija)
        self.edit_placeholder = tk.Frame(fixed_container, **theme_manager.get_style("card"))
        # Asegurar que el contenedor pueda expandirse para mostrar todo el contenido
        self.edit_placeholder.pack_forget()  # Oculto inicialmente
        
        # Separador visual fijo
        separator = tk.Frame(self, height=2, bg="#e0e0e0")
        separator.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        
        # Listado de gastos (área scrolleable)
        self._create_expenses_list()
    
    def _on_search_change(self):
        """Maneja cambios en el campo de búsqueda"""
        search_value = self.search_var.get()
        placeholder = "Buscar por nombre de inquilino o número de apartamento..."
        if search_value == placeholder or not search_value.strip():
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
        """Limpia todos los filtros"""
        self.category_filter_var.set("Todas")
        self.apartment_filter_var.set("Todos")
        self.year_filter_var.set("Todos")
        self.month_filter_var.set("Todos")
        self.search_var.set("Buscar por nombre de inquilino o número de apartamento...")
        self.filter_category = None
        self.filter_apartment = None
        self.filter_year = None
        self.filter_month = None
        self.search_text = ""
        
        # Ocultar formulario de edición si está visible
        self.editing_expense = None
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        self.edit_placeholder.pack_forget()
        
        self._create_expenses_list()
    
    def _create_expenses_list(self):
        """Crea el listado de gastos con scroll"""
        if hasattr(self, 'list_container'):
            self.list_container.destroy()
        
        # Contenedor con scroll
        self.list_container = tk.Frame(self, **theme_manager.get_style("card"))
        self.list_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        
        # Columnas (definir antes para usar en encabezado y contenido)
        columns = [
            ("ID", 5),
            ("Fecha", 12),
            ("Categoría", 15),
            ("Subtipo", 15),
            ("Apartamento", 12),
            ("Monto", 12),
            ("Descripción", 25),
            ("Acciones", 10)
        ]
        
        # ENCABEZADO FIJO (fuera del scroll)
        header_container = tk.Frame(self.list_container, bg="#f5f5f5", relief="solid", bd=1)
        header_container.pack(fill="x", pady=(0, 0))
        
        header = tk.Frame(header_container, bg="#f5f5f5")
        header.pack(fill="x")
        
        for idx, (col, width) in enumerate(columns):
            tk.Label(
                header,
                text=col,
                font=("Segoe UI", 10, "bold"),
                width=width,
                anchor="w",
                bg="#f5f5f5"
            ).grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
            header.grid_columnconfigure(idx, weight=1)
        
        # Contenedor para canvas y scrollbar
        scroll_container = tk.Frame(self.list_container, **theme_manager.get_style("frame"))
        scroll_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(scroll_container, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para el contenido (SOLO las filas de datos, sin encabezado)
        content_frame = tk.Frame(canvas, **theme_manager.get_style("card"))
        list_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", _on_frame_configure)
        
        def _on_canvas_configure(event):
            canvas_width = event.width
            if canvas_width > 0:
                canvas.itemconfig(list_window, width=canvas_width)
        
        canvas.bind("<Configure>", _on_canvas_configure)
        
        # Scroll con mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
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
            expenses = [e for e in expenses if e.get("apartamento") == self.filter_apartment]
        
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
        
        # Filas con efecto zebra
        zebra_colors = ("#ffffff", "#f0f4fa")
        
        if not expenses:
            # Mensaje cuando no hay gastos
            no_data_frame = tk.Frame(content_frame, bg="#ffffff")
            no_data_frame.grid(row=0, column=0, sticky="ew", pady=20)
            tk.Label(
                no_data_frame,
                text="No se encontraron gastos con los filtros seleccionados.",
                font=("Segoe UI", 11),
                fg="#666",
                bg="#ffffff"
            ).pack()
            content_frame.grid_columnconfigure(0, weight=1)
        else:
            for row_idx, expense in enumerate(expenses):
                bg_color = zebra_colors[row_idx % 2]
                row = tk.Frame(content_frame, bg=bg_color)
                row.grid(row=row_idx, column=0, sticky="ew")
                
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
                
                for col_idx, (val, (_, width)) in enumerate(zip(values, columns)):
                    tk.Label(
                        row,
                        text=val,
                        font=("Segoe UI", 10),
                        width=width,
                        anchor="w",
                        bg=bg_color
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
        
        # Configurar columnas del content_frame para alineación
        for idx in range(len(columns)):
            content_frame.grid_columnconfigure(idx, weight=1)
    
    def _show_edit_form(self, expense: Dict[str, Any]):
        """Muestra el formulario de edición para un gasto"""
        self.editing_expense = expense
        
        # Limpiar contenido anterior
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        
        # Mostrar el contenedor de edición dentro de fixed_container
        if not self.edit_placeholder.winfo_ismapped():
            self.edit_placeholder.pack(
                fill="both",
                expand=True,
                pady=(0, Spacing.MD)
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
        edit_form.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Asegurar que el contenedor se expanda para mostrar todo el contenido
        self.edit_placeholder.update_idletasks()
    
    def _cancel_edit(self):
        """Cancela la edición y oculta el formulario"""
        self.editing_expense = None
        
        # Limpiar y ocultar el formulario de edición
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        self.edit_placeholder.pack_forget()
        
        # Refrescar la lista
        self._create_expenses_list()
    
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
                messagebox.showinfo("Eliminado", "Gasto eliminado correctamente.")
                
                # Si estaba editando este gasto, cancelar la edición
                if self.editing_expense and self.editing_expense.get('id') == expense.get('id'):
                    self._cancel_edit()
                else:
                    self._create_expenses_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el gasto.")
    
    def _on_back(self):
        """Maneja el botón de volver"""
        if self.on_back:
            self.on_back()
