import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
if sys.platform == "win32":
    import winsound
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors, bind_combobox_dropdown_on_click
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service
from manager.app.logger import logger
from manager.app.ui.views.register_expense_view import DatePickerWidget

class EditDeletePaymentsView(tk.Frame):
    """Vista profesional para editar/eliminar pagos (independiente, duplicado de registrar pago)"""
    def __init__(self, parent, on_back=None, on_payment_saved=None, on_navigate_to_dashboard=None, on_register_new_payment=None, on_show_reports=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.payment_service = payment_service
        self.tenant_service = tenant_service
        self.on_back = on_back
        self.on_payment_saved = on_payment_saved  # Callback para actualizar otras vistas
        self.on_navigate_to_dashboard = on_navigate_to_dashboard  # Callback para navegar al dashboard
        self.on_register_new_payment = on_register_new_payment  # Callback para abrir registrar nuevo pago
        self.on_show_reports = on_show_reports  # Callback para abrir reportes de pagos
        self.selected_tenant = None
        self.editing_payment = None
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        # Contenedor: búsqueda y formulario de edición
        fixed_container = tk.Frame(self, bg=cb)
        fixed_container.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, 4))
        search_frame = tk.Frame(fixed_container, bg=cb)
        search_frame.pack(fill="x", pady=(0, 2))
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
        self.edit_placeholder = tk.Frame(fixed_container, bg=cb)
        self.edit_placeholder.pack_forget()
        # Separador y listado con poco espacio entre búsqueda y tabla
        separator = tk.Frame(self, height=2, bg=theme.get("border_light", "#e0e0e0"))
        separator.pack(fill="x", padx=Spacing.LG, pady=(0, 4))
        self._create_payments_list()
        # Posicionar cursor en el cuadro de búsqueda al abrir la vista
        self.after(150, self._focus_search_entry)

    def _create_action_cards(self, parent):
        """Dos cards del mismo tamaño: Registrar nuevo pago y Reportes."""
        cb = self._content_bg
        colors = get_module_colors("pagos")
        card_bg = colors.get("primary", "#166534")
        card_hover = colors.get("hover", "#15803d")
        cards_frame = tk.Frame(parent, bg=cb)
        cards_frame.pack(fill="x", padx=Spacing.LG, pady=(0, 8))
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        btn_register = tk.Button(
            cards_frame,
            text=f"{Icons.PAYMENT_RECEIVED} Registrar nuevo pago",
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
        """Abre ventana compacta para registrar pago usando el inquilino del filtro (sin cambiar de vista)."""
        from .payments_view import PaymentModal
        def _after_save(_data):
            if self.on_payment_saved:
                self.on_payment_saved()
            self._create_payments_list()
        PaymentModal(
            self,
            self.tenants,
            on_save=_after_save,
            preselected_tenant=self.selected_tenant,
            compact=True,
        )

    def _on_reports_card(self):
        if self.on_show_reports:
            self.on_show_reports()

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

        self.list_container = tk.Frame(self, bg=cb)
        self.list_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(4, Spacing.LG))

        # Pre-cargar datos una sola vez
        pagos = self.payment_service.get_all_payments()
        if self.selected_tenant:
            pagos = [p for p in pagos if p['id_inquilino'] == self.selected_tenant['id']]
        pagos = list(reversed(pagos))

        try:
            all_apts = apartment_service.get_all_apartments()
            apt_map = {a["id"]: a for a in all_apts if "id" in a}
        except Exception:
            apt_map = {}
        tenant_apt_map = {t["id"]: apt_map.get(t.get("apartamento")) for t in self.tenants}

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
        columns = ("inquilino", "fecha", "monto", "metodo", "observaciones")
        self._tree = ttk.Treeview(
            self.list_container, columns=columns,
            show="headings", selectmode="browse",
        )
        col_cfg = [
            ("inquilino",     "Inquilino",      220),
            ("fecha",         "Fecha de pago",  110),
            ("monto",         "Monto",          100),
            ("metodo",        "Método",          90),
            ("observaciones", "Observaciones",  260),
        ]
        for col_id, heading, width in col_cfg:
            self._tree.heading(col_id, text=heading)
            self._tree.column(col_id, width=width, minwidth=60, anchor="w")

        # Colores zebra
        self._tree.tag_configure("odd",  background=cb)
        self._tree.tag_configure("even", background=theme.get("bg_tertiary", "#f0f4fa"))

        scrollbar = ttk.Scrollbar(self.list_container, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Poblar
        self._payments_index = {}
        if not pagos:
            self._tree.insert("", "end", values=(
                "No hay pagos registrados.", "", "", "", "",
            ))
        else:
            for idx, payment in enumerate(pagos):
                apt = tenant_apt_map.get(payment['id_inquilino'])
                apto = apt['number'] if (apt and 'number' in apt) else ''
                tag = "odd" if idx % 2 == 0 else "even"
                iid = self._tree.insert("", "end", tags=(tag,), values=(
                    f"{payment.get('nombre_inquilino', '')} (Apt. {apto})",
                    payment.get('fecha_pago', ''),
                    f"${payment.get('monto', 0):,.2f}",
                    payment.get('metodo', ''),
                    payment.get('observaciones', ''),
                ))
                self._payments_index[iid] = payment

        # Doble clic → editar | Supr → eliminar
        self._tree.bind("<Double-1>", self._on_tree_double_click)
        self._tree.bind("<Delete>",   self._on_tree_delete_key)

        # Dar foco al Treeview para que el primer clic seleccione la fila directamente
        self.after(150, lambda: self._tree.focus_set() if self._tree.winfo_exists() else None)

    def _on_tree_double_click(self, event=None):
        sel = self._tree.selection()
        if not sel:
            return
        payment = self._payments_index.get(sel[0])
        if payment:
            self._show_edit_form(payment)

    def _on_tree_delete_key(self, event=None):
        sel = self._tree.selection()
        if not sel:
            return
        payment = self._payments_index.get(sel[0])
        if payment:
            self._delete_payment(payment)

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
        tk.Entry(row2, textvariable=monto_var, width=27).pack(side="left", **row_opts)
        # Método
        row3 = tk.Frame(self.edit_placeholder, bg=cb)
        row3.pack(fill="x", pady=1)
        tk.Label(row3, text="Método:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        metodo_var = tk.StringVar(value=self.editing_payment['metodo'])
        metodo_combo = ttk.Combobox(row3, textvariable=metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=24)
        metodo_combo.pack(side="left", **row_opts)
        bind_combobox_dropdown_on_click(metodo_combo)
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
        if sys.platform == "win32":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)

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
            if not self.winfo_exists():
                return
            success = self.payment_service.delete_payment(payment['id'])
            if success:
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
                if self.on_payment_saved:
                    self.on_payment_saved()
                if self.winfo_exists():
                    self._create_payments_list()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pago.")

    def _create_navigation_buttons(self, parent, on_back_command, show_back_button=False):
        """Crea el botón Dashboard y opcionalmente Volver (en esta vista solo Dashboard)."""
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
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
        
        # Botón "Volver" (solo si se pide; en esta vista no se muestra, ya hay Dashboard)
        if show_back_button:
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