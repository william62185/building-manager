import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service
from manager.app.logger import logger
from manager.app.ui.views.register_expense_view import DatePickerWidget

class EditDeletePaymentsView(tk.Frame):
    """Vista profesional para editar/eliminar pagos (independiente, duplicado de registrar pago)"""
    def __init__(self, parent, on_back=None, on_payment_saved=None, on_navigate_to_dashboard=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.payment_service = payment_service
        self.tenant_service = tenant_service
        self.on_back = on_back
        self.on_payment_saved = on_payment_saved  # Callback para actualizar otras vistas
        self.on_navigate_to_dashboard = on_navigate_to_dashboard  # Callback para navegar al dashboard
        self.selected_tenant = None
        self.editing_payment = None
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        # Header
        header = tk.Frame(self, bg=cb)
        header.pack(fill="x", pady=(0, Spacing.LG))
        
        # Título a la izquierda
        title = tk.Label(header, text="Editar/Eliminar Pagos", font=("Segoe UI", 16, "bold"), bg=cb, fg=theme["text_primary"])
        title.pack(side="left", padx=(0, Spacing.LG))
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, bg=cb)
        buttons_frame.pack(side="right")
        
        # Agregar botones Volver y Dashboard
        self._create_navigation_buttons(buttons_frame, self._on_back)
        # Contenedor fijo (igual que en gastos): búsqueda y formulario de edición
        fixed_container = tk.Frame(self, bg=cb)
        fixed_container.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        search_frame = tk.Frame(fixed_container, bg=cb)
        search_frame.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(search_frame, text="Búsqueda:", font=("Segoe UI", 11), bg=cb, fg=theme["text_primary"]).pack(side="left", padx=(0, Spacing.SM))
        self.tenants = self.tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            search_frame,
            self.tenants,
            on_select=self._on_tenant_selected,
            width=35,
            entry_pady=8,
            entry_font=("Segoe UI", 12),
            bg=cb
        )
        self.tenant_autocomplete.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        btn_clear = ModernButton(search_frame, text="Limpiar búsqueda", icon=Icons.CANCEL, style="warning", command=self._clear_tenant_search, small=True, fg="#000000")
        btn_clear.pack(side="left", padx=(Spacing.MD, 0))
        # Placeholder para el formulario de edición (igual que en gastos)
        self.edit_placeholder = tk.Frame(fixed_container, bg=cb)
        self.edit_placeholder.pack_forget()
        # Separador y listado (mismo orden que en gastos)
        separator = tk.Frame(self, height=2, bg=theme.get("border_light", "#e0e0e0"))
        separator.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        self._create_payments_list()
        # Posicionar cursor en el cuadro de búsqueda al abrir la vista
        self.after(150, self._focus_search_entry)

    def _focus_search_entry(self):
        """Coloca el foco en el cuadro de búsqueda al abrir la vista Editar/Eliminar pagos."""
        if hasattr(self, "tenant_autocomplete") and hasattr(self.tenant_autocomplete, "entry"):
            if self.tenant_autocomplete.entry.winfo_exists():
                self.tenant_autocomplete.entry.focus_set()

    def _on_tenant_selected(self, tenant):
        self.selected_tenant = tenant
        self._create_payments_list()

    def _clear_tenant_search(self):
        self.tenant_autocomplete.set_tenants(self.tenants)
        self.selected_tenant = None
        # Ocultar el formulario de edición si está visible
        self.editing_payment = None
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        self.edit_placeholder.pack_forget()
        self._create_payments_list()

    def _create_payments_list(self):
        if hasattr(self, 'list_container'):
            self.list_container.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        bg_alt = theme.get("bg_tertiary", "#f0f4fa")
        header_bg = "#dcfce7"
        header_fg = "#166534"
        columns = [
            ("Inquilino", 20),
            ("Fecha de pago", 14),
            ("Monto", 14),
            ("Método", 10),
            ("Observaciones", 36),
            ("Acciones", 10)
        ]
        # --- Un solo grid (como en gastos): encabezado y cuerpo comparten columnas para alineación exacta ---
        self.list_container = tk.Frame(self, bg=cb)
        self.list_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        sep_color = theme.get("border_light", "#d1d5db")
        table_grid = tk.Frame(self.list_container, bg=cb)
        table_grid.pack(fill="both", expand=True)
        for i in range(6):
            table_grid.grid_columnconfigure(i, weight=1)
        table_grid.grid_columnconfigure(6, weight=0, minsize=17)
        # Fila 0: encabezado (columnas 0-5)
        header_frame = tk.Frame(table_grid, bg=header_bg)
        header_frame.grid(row=0, column=0, columnspan=6, sticky="nsew")
        for idx in range(6):
            header_frame.grid_columnconfigure(idx, weight=1)
        col_anchors = ["w", "w", "w", "w", "w", "w"]
        for idx, (col, width) in enumerate(columns):
            anc = col_anchors[idx] if idx < len(col_anchors) else "w"
            tk.Label(header_frame, text=col, font=("Segoe UI", 10, "bold"), width=width, anchor=anc, bg=header_bg, fg=header_fg).grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
        scrollbar_header_placeholder = tk.Frame(table_grid, width=17, bg=header_bg)
        scrollbar_header_placeholder.grid(row=0, column=6, sticky="ns")
        scrollbar_header_placeholder.pack_propagate(False)
        # Fila 1: línea separadora
        header_sep = tk.Frame(table_grid, height=2, bg=sep_color)
        header_sep.grid(row=1, column=0, columnspan=6, sticky="ew")
        header_sep.grid_propagate(False)
        tk.Frame(table_grid, width=17, bg=cb).grid(row=1, column=6)
        # Fila 2: canvas (columnas 0-5) + scrollbar (columna 6)
        table_grid.grid_rowconfigure(2, weight=1)
        canvas_holder = tk.Frame(table_grid, bg=cb)
        canvas_holder.grid(row=2, column=0, columnspan=6, sticky="nsew")
        canvas = tk.Canvas(canvas_holder, bg=cb, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(table_grid, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=2, column=6, sticky="ns")
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
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        content_frame.bind('<Enter>', _bind_mousewheel)
        content_frame.bind('<Leave>', _unbind_mousewheel)
        # --- FILAS DEL LISTADO ---
        pagos = self.payment_service.get_all_payments()
        if self.selected_tenant:
            pagos = [p for p in pagos if p['id_inquilino'] == self.selected_tenant['id']]
        pagos = list(reversed(pagos))
        zebra_colors = (cb, bg_alt)
        if not pagos:
            no_data_frame = tk.Frame(content_frame, bg=cb)
            no_data_frame.grid(row=0, column=0, columnspan=6, sticky="ew", pady=20)
            tk.Label(
                no_data_frame,
                text="No se encontraron pagos." if self.selected_tenant else "No hay pagos registrados.",
                font=("Segoe UI", 11),
                fg=theme.get("text_secondary", "#666"),
                bg=cb
            ).pack()
            content_frame.grid_columnconfigure(0, weight=1)
        else:
            for row_idx, payment in enumerate(pagos):
                bg_color = zebra_colors[row_idx % 2]
                row = tk.Frame(content_frame, bg=bg_color)
                row.grid(row=row_idx, column=0, columnspan=6, sticky="ew")
                nombre = payment.get('nombre_inquilino', '')
                apto = ''
                for t in self.tenants:
                    if t['id'] == payment['id_inquilino']:
                        apt_id = t.get('apartamento', '')
                        if apt_id:
                            try:
                                apt = apartment_service.get_apartment_by_id(int(apt_id))
                                apto = apt['number'] if (apt and 'number' in apt) else str(apt_id)
                            except Exception:
                                apto = str(apt_id)
                        break
                values = [
                    f"{nombre} (Apt. {apto})",
                    f"{payment['fecha_pago']}",
                    f"${payment['monto']:,.2f}",
                    f"{payment['metodo']}",
                    f"{payment.get('observaciones','')}"
                ]
                for idx in range(len(columns)):
                    row.grid_columnconfigure(idx, weight=1)
                data_anchors = ["w", "w", "w", "w", "w"]
                for col_idx, (val, (_, width)) in enumerate(zip(values, columns)):
                    anc = data_anchors[col_idx] if col_idx < len(data_anchors) else "w"
                    tk.Label(row, text=val, font=("Segoe UI", 10), width=width, anchor=anc, bg=bg_color, fg=theme["text_primary"]).grid(row=0, column=col_idx, padx=(0, 1), sticky="nsew")
                actions_frame = tk.Frame(row, bg=bg_color)
                actions_frame.grid(row=0, column=len(values), padx=(0, 1), sticky="nsew")
                btn_edit = tk.Button(actions_frame, text=Icons.EDIT, font=("Segoe UI", 12), fg="#1976d2", bg=bg_color, bd=0, relief="flat", cursor="hand2", command=lambda p=payment: self._show_edit_form(p))
                btn_edit.pack(side="left", padx=(0, 6))
                btn_delete = tk.Button(actions_frame, text=Icons.DELETE, font=("Segoe UI", 12), fg="#d32f2f", bg=bg_color, bd=0, relief="flat", cursor="hand2", command=lambda p=payment: self._delete_payment(p))
                btn_delete.pack(side="left")
                row.grid_columnconfigure(len(values), weight=1)
        for idx in range(len(columns)):
            content_frame.grid_columnconfigure(idx, weight=1)

    def _show_edit_form(self, payment):
        self.editing_payment = payment
        # Seleccionar el inquilino correspondiente en el autocomplete
        tenant = next((t for t in self.tenants if t['id'] == payment['id_inquilino']), None)
        if tenant:
            self.tenant_autocomplete._select_tenant(tenant)
        # Mostrar el contenedor de edición dentro de fixed_container (como en gastos)
        if not self.edit_placeholder.winfo_ismapped():
            self.edit_placeholder.pack(fill="x", pady=(Spacing.SM, Spacing.MD))
        self._build_edit_payment_form()

    def _build_edit_payment_form(self):
        # Destruir cualquier formulario anterior
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        row_opts = {'padx': (0, 8), 'pady': 2}
        # Fecha (con mini selector de calendario)
        row1 = tk.Frame(self.edit_placeholder, bg=cb)
        row1.pack(fill="x", pady=1)
        tk.Label(row1, text="Fecha de pago (DD/MM/YYYY):", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        fecha_var = tk.StringVar(value=self.editing_payment['fecha_pago'])
        date_picker = DatePickerWidget(row1)
        date_picker.pack(side="left", **row_opts)
        date_picker.set(fecha_var.get())
        def _on_date_change(event=None):
            val = date_picker.get()
            if val:
                fecha_var.set(val)
        date_picker.date_entry.bind("<KeyRelease>", _on_date_change)
        date_picker.date_entry.bind("<FocusOut>", _on_date_change)
        _orig_select = date_picker._select_date
        _orig_today = date_picker._select_today
        def _wrapped_select(day):
            _orig_select(day)
            fecha_var.set(date_picker.get())
        def _wrapped_today():
            _orig_today()
            fecha_var.set(date_picker.get())
        date_picker._select_date = _wrapped_select
        date_picker._select_today = _wrapped_today
        # Monto
        row2 = tk.Frame(self.edit_placeholder, bg=cb)
        row2.pack(fill="x", pady=1)
        tk.Label(row2, text="Monto:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        monto_var = tk.StringVar(value=str(self.editing_payment['monto']))
        tk.Entry(row2, textvariable=monto_var, width=19).pack(side="left", **row_opts)
        # Método
        row3 = tk.Frame(self.edit_placeholder, bg=cb)
        row3.pack(fill="x", pady=1)
        tk.Label(row3, text="Método:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        metodo_var = tk.StringVar(value=self.editing_payment['metodo'])
        metodo_combo = ttk.Combobox(row3, textvariable=metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=16)
        metodo_combo.pack(side="left", **row_opts)
        # Observaciones
        row4 = tk.Frame(self.edit_placeholder, bg=cb)
        row4.pack(fill="x", pady=1)
        tk.Label(row4, text="Observaciones:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        obs_var = tk.StringVar(value=self.editing_payment.get('observaciones', ''))
        tk.Entry(row4, textvariable=obs_var, width=40).pack(side="left", **row_opts)
        # Botones guardar/cancelar
        btns = tk.Frame(self.edit_placeholder, bg=cb)
        btns.pack(pady=(4, 0), anchor="w")
        btn_save = tk.Button(btns, text="Guardar cambios", command=lambda: self._save_edit_payment(fecha_var, monto_var, metodo_var, obs_var))
        btn_save.pack(side="left", padx=(0, 8))
        btn_cancel = tk.Button(btns, text="Cancelar", command=self._cancel_edit)
        btn_cancel.pack(side="left")

    def _save_edit_payment(self, fecha_var, monto_var, metodo_var, obs_var):
        # Validaciones básicas (puedes expandirlas)
        try:
            fecha = fecha_var.get()
            monto = float(monto_var.get())
            metodo = metodo_var.get()
            obs = obs_var.get()
            if not fecha or not metodo:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Datos inválidos.")
            return
        data = self.editing_payment.copy()
        data['fecha_pago'] = fecha
        data['monto'] = monto
        data['metodo'] = metodo
        data['observaciones'] = obs
        self.payment_service.update_payment(self.editing_payment['id'], data)
        messagebox.showinfo("Éxito", "Pago actualizado correctamente.")
        
        # Llamar callback para actualizar otras vistas (como la lista de inquilinos)
        if self.on_payment_saved:
            self.on_payment_saved()
        
        self.editing_payment = None
        # Limpiar el formulario de edición y ocultar el contenedor
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        self.edit_placeholder.pack_forget()
        self._create_payments_list()

    def _cancel_edit(self):
        self.editing_payment = None
        # Limpiar el formulario de edición y ocultar el contenedor
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        self.edit_placeholder.pack_forget()
        # Limpiar el textbox de búsqueda de inquilino
        self.tenant_autocomplete.set_tenants(self.tenants)
        # Mostrar todos los pagos en el listado
        self.selected_tenant = None
        self._create_payments_list()

    def _delete_payment(self, payment):
        if messagebox.askyesno("Eliminar pago", "¿Seguro que deseas eliminar este pago?"):
            success = self.payment_service.delete_payment(payment['id'])
            if success:
                messagebox.showinfo("Eliminado", "Pago eliminado correctamente.")
                
                # Llamar callback para actualizar otras vistas (como la lista de inquilinos)
                if self.on_payment_saved:
                    self.on_payment_saved()
                
                self._create_payments_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pago.")

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
        
        # Colores verdes para módulo de pagos
        colors = get_module_colors("pagos")
        green_primary = colors["primary"]
        green_hover = colors["hover"]
        green_light = colors["light"]
        green_text = colors["text"]
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard principal)
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
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=green_primary,
            hover_bg=green_light,
            hover_fg=green_text,
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
            bg_color=green_primary,
            fg_color="white",
            hover_bg=green_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")

    def _on_back(self):
        if self.on_back:
            self.on_back() 