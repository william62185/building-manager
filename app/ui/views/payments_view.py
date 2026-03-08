import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors, bind_combobox_dropdown_on_click
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard, ModernSeparator
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
import webbrowser
from .edit_delete_payments_view import EditDeletePaymentsView
from .register_expense_view import DatePickerWidget
from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.logger import logger
from manager.app.presenters.payment_presenter import PaymentPresenter

class PaymentsView(tk.Frame):
    """Vista profesional para gestión de pagos de inquilinos"""
    def __init__(self, parent, on_back=None, preselected_tenant=None, on_payment_saved=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.payment_service = payment_service
        self.tenant_service = tenant_service
        self.on_back = on_back
        self.preselected_tenant = preselected_tenant
        self.on_payment_saved = on_payment_saved  # Callback para actualizar otras vistas
        self.presenter = PaymentPresenter(on_back=on_back, on_payment_saved=on_payment_saved)
        # Abrir directamente la vista de listado/edición (sin menú de 3 cards)
        self._show_edit_delete_payments()

    
    def _create_navigation_buttons(self, parent, on_back_command, show_back_button=True):
        """Crea los botones Volver y Dashboard con estilo moderno y colores verdes del módulo de pagos"""
        # Colores verdes para módulo de pagos
        colors = get_module_colors("pagos")
        green_primary = colors["primary"]
        green_hover = colors["hover"]
        green_light = colors["light"]
        green_text = colors["text"]
        
        # Botón "Volver" (solo si show_back_button es True)
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
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard)
        def go_to_dashboard():
            if self.on_back:
                self.on_back()  # on_back ya navega al dashboard desde main_window
        
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

    def _show_register_payment(self, preselected_tenant=None):
        # Cambiar el título global de la ventana
        try:
            self.master.master.page_title.configure(text="Registrar pagos")
        except Exception:
            pass
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(bg=self._content_bg)
        theme = theme_manager.themes[theme_manager.current_theme]
        # Header con búsqueda y botón volver en la misma línea
        header = tk.Frame(self, bg=self._content_bg)
        header.pack(fill="x", pady=(0, 10), padx=(2, 2))
        # Frame izquierdo: búsqueda y limpiar
        left_header = tk.Frame(header, bg=self._content_bg)
        left_header.pack(side="left", fill="x", expand=True)
        tk.Label(
            left_header,
            text="Buscar inquilino:",
            font=("Segoe UI", 14, "bold"),
            bg=self._content_bg,
            fg=theme["text_primary"]
        ).pack(side="left")
        self.tenants = self.tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            left_header,
            self.tenants,
            on_select=self._on_register_tenant_selected,
            width=35,
            entry_pady=8,
            entry_font=("Segoe UI", 12),
            bg=self._content_bg
        )
        self.tenant_autocomplete.pack(side="left", fill="x", expand=True, padx=(2, 0))
        btn_clear = ModernButton(left_header, text="Limpiar búsqueda", icon=Icons.CANCEL, style="warning", command=self._clear_tenant_search, small=True, fg="#000000")
        btn_clear.pack(side="left", padx=(2, Spacing.MD))
        # Frame derecho: botones de navegación
        buttons_frame = tk.Frame(header, bg=self._content_bg)
        buttons_frame.pack(side="right", pady=(0, 0))
        self._create_navigation_buttons(buttons_frame, self._restore_global_title)
        # Inicializar variables del formulario antes de construir el formulario
        self.fecha_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.monto_var = tk.StringVar()
        self.metodo_var = tk.StringVar(value="Efectivo")
        self.obs_var = tk.StringVar()
        # Limpiar selección de inquilino si no hay preseleccionado
        if preselected_tenant is None:
            self.selected_tenant = None
        else:
            # Buscar el inquilino por ID en self.tenants para asegurar coincidencia por referencia
            tenant_id = preselected_tenant.get('id')
            match = next((t for t in self.tenants if t.get('id') == tenant_id), None)
            self.selected_tenant = match if match else preselected_tenant
        # Sección central: formulario de pago (sin listado)
        self.form_frame = tk.Frame(self, bg=self._content_bg)
        self.form_frame.pack(fill="both", expand=True, padx=2, pady=(0, Spacing.LG))
        self._build_register_payment_form()
        # Si hay un inquilino preseleccionado, autocompletar el campo
        if self.selected_tenant:
            self.tenant_autocomplete._select_tenant(self.selected_tenant)
        # Posicionar cursor en el cuadro de búsqueda al abrir la vista
        self.after(150, self._focus_search_entry_register)

    def _focus_search_entry_register(self):
        """Coloca el foco en el cuadro de búsqueda de inquilino (vista Registrar nuevo pago)."""
        if hasattr(self, "tenant_autocomplete") and hasattr(self.tenant_autocomplete, "entry"):
            if self.tenant_autocomplete.entry.winfo_exists():
                self.tenant_autocomplete.entry.focus_set()

    def _restore_global_title(self):
        try:
            self.master.master.page_title.configure(text="Gestión de Pagos")
        except Exception:
            pass
        self._show_edit_delete_payments()

    def _get_tenant_apartment_display(self, tenant):
        """Devuelve texto tipo 'Edificio X - 101' o 'N/A' para el inquilino."""
        if not tenant:
            return "—"
        apt_id = tenant.get("apartamento", None)
        if apt_id is None:
            return "—"
        try:
            apt_id = int(apt_id) if isinstance(apt_id, str) and apt_id.isdigit() else apt_id
            apt = apartment_service.get_apartment_by_id(apt_id)
        except (TypeError, ValueError):
            return "—"
        if not apt:
            return "—"
        building = None
        if hasattr(building_service, "get_building_by_id"):
            building = building_service.get_building_by_id(apt.get("building_id"))
        if not building:
            all_buildings = building_service.get_all_buildings()
            building = next((b for b in all_buildings if b.get("id") == apt.get("building_id")), None)
        building_name = building.get("name", "") if building else ""
        tipo = apt.get("unit_type", "Apartamento Estándar")
        numero = apt.get("number", "")
        if building_name:
            return f"{building_name} - {tipo} {numero}" if tipo != "Apartamento Estándar" else f"{building_name} - {numero}"
        return f"{tipo} {numero}" if tipo != "Apartamento Estándar" else str(numero)

    def _build_register_payment_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        row_opts = {'padx': (0, 12), 'pady': 2}
        # Título de la sección
        tk.Label(
            self.form_frame,
            text="Datos del pago",
            font=("Segoe UI", 12, "bold"),
            bg=cb,
            fg=theme["text_primary"]
        ).pack(anchor="w", pady=(0, Spacing.SM))
        # Contenedor de campos: mismo fondo que la vista, borde sutil en tono oliva
        border_color = "#c4bc8a"
        card_wrap = tk.Frame(self.form_frame, bg=border_color, padx=1, pady=1)
        card_wrap.pack(fill="x", pady=(0, Spacing.MD))
        card = tk.Frame(card_wrap, bg=cb, padx=Spacing.LG, pady=Spacing.LG)
        card.pack(fill="x")
        # Variables para datos que se arrastran del inquilino seleccionado
        self._var_apt_display = tk.StringVar(value=self._get_tenant_apartment_display(getattr(self, "selected_tenant", None)))
        self._var_tenant_name = tk.StringVar(value=(self.selected_tenant.get("nombre", "—") if getattr(self, "selected_tenant", None) else "—"))
        # Apartamento/Unidad (solo lectura)
        row_apt = tk.Frame(card, bg=cb)
        row_apt.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row_apt, text="Apartamento/Unidad:", width=24, anchor="w", bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Label(row_apt, textvariable=self._var_apt_display, anchor="w", bg=cb, fg=theme["text_secondary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        # Nombre del inquilino (solo lectura)
        row_name = tk.Frame(card, bg=cb)
        row_name.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row_name, text="Nombre del inquilino:", width=24, anchor="w", bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Label(row_name, textvariable=self._var_tenant_name, anchor="w", bg=cb, fg=theme["text_secondary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        # Fecha (con mini selector de calendario)
        row1 = tk.Frame(card, bg=cb)
        row1.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row1, text="Fecha de pago (DD/MM/YYYY):", width=24, anchor="w", bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        self.date_picker = DatePickerWidget(row1)
        self.date_picker.pack(side="left", **row_opts)
        self.date_picker.set(self.fecha_var.get())
        def _on_date_change(event=None):
            val = self.date_picker.get()
            if val:
                self.fecha_var.set(val)
        self.date_picker.date_entry.bind("<KeyRelease>", _on_date_change)
        self.date_picker.date_entry.bind("<FocusOut>", _on_date_change)
        _orig_select = self.date_picker._select_date
        _orig_today = self.date_picker._select_today
        def _wrapped_select(day):
            _orig_select(day)
            self.fecha_var.set(self.date_picker.get())
        def _wrapped_today():
            _orig_today()
            self.fecha_var.set(self.date_picker.get())
        self.date_picker._select_date = _wrapped_select
        self.date_picker._select_today = _wrapped_today
        # Monto
        row2 = tk.Frame(card, bg=cb)
        row2.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row2, text="Monto:", width=24, anchor="w", bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Entry(row2, textvariable=self.monto_var, width=28, font=("Segoe UI", 10)).pack(side="left", **row_opts)
        # Método
        row3 = tk.Frame(card, bg=cb)
        row3.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row3, text="Método:", width=24, anchor="w", bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        metodo_combo = ttk.Combobox(row3, textvariable=self.metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=26, font=("Segoe UI", 10))
        metodo_combo.pack(side="left", **row_opts)
        bind_combobox_dropdown_on_click(metodo_combo)
        # Observaciones
        row4 = tk.Frame(card, bg=cb)
        row4.pack(fill="x", pady=(0, Spacing.MD))
        tk.Label(row4, text="Observaciones:", width=24, anchor="w", bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Entry(row4, textvariable=self.obs_var, width=42, font=("Segoe UI", 10)).pack(side="left", **row_opts)
        # Botón Registrar Pago debajo del card
        btn_save = tk.Button(
            self.form_frame,
            text="Registrar Pago",
            command=self._save_register_payment,
            bg="#22c55e",
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        btn_save.pack(pady=(Spacing.SM, 0), anchor="w")
        def on_enter_save(e):
            btn_save.configure(bg="#16a34a")
        def on_leave_save(e):
            btn_save.configure(bg="#22c55e")
        btn_save.bind("<Enter>", on_enter_save)
        btn_save.bind("<Leave>", on_leave_save)

    def _clear_tenant_search(self):
        self.tenant_autocomplete.set_tenants(self.tenants)
        self.selected_tenant = None
        if hasattr(self, "_var_apt_display"):
            self._var_apt_display.set("—")
        if hasattr(self, "_var_tenant_name"):
            self._var_tenant_name.set("—")
        self.monto_var.set("")
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        if hasattr(self, "date_picker") and self.date_picker.winfo_exists():
            self.date_picker.set(self.fecha_var.get())
        self.metodo_var.set("Efectivo")
        self.obs_var.set("")

    def _get_all_payments(self):
        pagos = self.payment_service.get_all_payments()
        # Mostrar el último pago registrado primero (orden de registro, no por fecha)
        return list(reversed(pagos))

    def _on_register_tenant_selected(self, tenant):
        self.selected_tenant = tenant
        if hasattr(self, "_var_apt_display"):
            self._var_apt_display.set(self._get_tenant_apartment_display(tenant))
        if hasattr(self, "_var_tenant_name"):
            self._var_tenant_name.set(tenant.get("nombre", "—"))
        if hasattr(self, 'monto_var'):
            self.monto_var.set(str(tenant.get('valor_arriendo', '')))

    def _display_register_payments(self, payments):
        if not hasattr(self, "list_frame") or not self.list_frame.winfo_exists():
            return
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        bg_alt = theme.get("bg_tertiary", "#f0f4fa")
        columns = getattr(self, '_table_columns', [
            ("Inquilino", 22), ("Fecha de pago", 12), ("Monto", 14), ("Método", 12), ("Observaciones", 38)
        ])
        # Solo filas de datos (el encabezado está fijo en list_header_frame)
        table_frame = tk.Frame(self.list_frame, bg=cb)
        table_frame.pack(fill="x", pady=(0, 2))
        for idx in range(len(columns)):
            table_frame.grid_columnconfigure(idx, weight=1)
        if not payments:
            tk.Label(table_frame, text="No hay pagos registrados.", font=("Segoe UI", 11), fg=theme["text_secondary"], bg=cb).grid(row=0, column=0, columnspan=len(columns), pady=10, sticky="w")
            return
        zebra_colors = (cb, bg_alt)
        for row_idx, payment in enumerate(payments):
            bg_color = zebra_colors[row_idx % 2]
            row_bg = tk.Frame(table_frame, bg=bg_color)
            row_bg.grid(row=row_idx, column=0, columnspan=len(columns), sticky="nsew")
            nombre = payment.get('nombre_inquilino', '')
            apto = ''
            for t in self.tenants:
                if t['id'] == payment['id_inquilino']:
                    apt_id = t.get('apartamento', '')
                    if apt_id:
                        try:
                            apt = apartment_service.get_apartment_by_id(int(apt_id))
                            if apt and 'number' in apt:
                                apto = apt['number']
                            else:
                                apto = apt_id
                        except Exception:
                            apto = apt_id
                    break
            values = [
                f"{nombre} (Apt. {apto})",
                f"{payment['fecha_pago']}",
                f"${payment['monto']:,.2f}",
                f"{payment['metodo']}",
                f"{payment.get('observaciones','')}"
            ]
            for col_idx, (val, (_, width)) in enumerate(zip(values, columns)):
                tk.Label(table_frame, text=val, font=("Segoe UI", 10), width=width, anchor="w", bg=bg_color).grid(row=row_idx, column=col_idx, padx=(0, 1), sticky="nsew")

    def _save_register_payment(self):
        if not hasattr(self, 'selected_tenant') or not self.selected_tenant:
            messagebox.showerror("Error", "Debe seleccionar un inquilino.")
            return
        fecha_str = self.date_picker.get() if (hasattr(self, "date_picker") and self.date_picker.winfo_exists()) else self.fecha_var.get()
        if fecha_str:
            self.fecha_var.set(fecha_str)
        if not self.fecha_var.get():
            messagebox.showerror("Error", "Debe ingresar la fecha de pago.")
            return
        try:
            datetime.strptime(self.fecha_var.get(), "%d/%m/%Y")
        except Exception:
            messagebox.showerror("Error", "La fecha debe tener formato DD/MM/YYYY.")
            return
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return
        data = {
            "id_inquilino": self.selected_tenant['id'],
            "nombre_inquilino": self.selected_tenant['nombre'],
            "fecha_pago": self.fecha_var.get(),
            "monto": float(self.monto_var.get()),
            "metodo": self.metodo_var.get(),
            "observaciones": self.obs_var.get()
        }
        
        # Verificar si ya existe un pago similar (prevenir duplicados)
        existing_payments = self.payment_service.get_payments_by_tenant(data.get('id_inquilino'))
        for payment in existing_payments:
            if (payment.get('fecha_pago') == data.get('fecha_pago') and 
                payment.get('monto') == data.get('monto')):
                messagebox.showwarning("Advertencia", "Ya existe un pago con la misma fecha y monto para este inquilino.")
                return
        
        # Registrar el pago (esto también actualiza automáticamente el estado del inquilino)
        payment_result = self.payment_service.add_payment(data)
        
        # Generar PDF profesional del recibo
        pdf_path = self._generate_payment_receipt_pdf(data)
        # Mostrar mensaje y preguntar si desea abrir el PDF
        if messagebox.askyesno("Recibo generado", f"Recibo PDF generado exitosamente:\n{pdf_path}\n\n¿Desea abrir el recibo ahora?"):
            webbrowser.open_new(pdf_path)
        messagebox.showinfo("Éxito", "Pago registrado correctamente.")
        
        # Llamar callback para actualizar otras vistas DESPUÉS de que todo se guarde
        if self.on_payment_saved:
            self.on_payment_saved()
        
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        if hasattr(self, "date_picker") and self.date_picker.winfo_exists():
            self.date_picker.set(self.fecha_var.get())
        self.monto_var.set(str(self.selected_tenant.get('valor_arriendo', '')))
        self.metodo_var.set("Efectivo")
        self.obs_var.set("")

    def _generate_payment_receipt_pdf(self, pago):
        from manager.app.paths_config import DOCUMENTOS_INQUILINOS_DIR, ensure_dirs, get_tenant_document_folder_name
        from manager.app.receipt_pdf import generate_payment_receipt_pdf
        ensure_dirs()
        tenant = self.selected_tenant or {}
        folder_name = get_tenant_document_folder_name(tenant)
        tenant_dir = DOCUMENTOS_INQUILINOS_DIR / folder_name
        tenant_dir.mkdir(parents=True, exist_ok=True)
        fecha = pago.get("fecha_pago", "").replace("/", "-")
        filepath = str(tenant_dir / f"recibo_{fecha}.pdf")
        return generate_payment_receipt_pdf(pago, tenant, filepath)

    def _show_edit_delete_payments(self):
        from .edit_delete_payments_view import EditDeletePaymentsView
        # Limpiar vista y mostrar la vista profesional de edición/eliminación de pagos
        for widget in self.winfo_children():
            widget.destroy()
        
        # Función para navegar al dashboard principal
        def go_to_dashboard():
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
            # Fallback: usar on_back si está disponible
            if self.on_back:
                self.on_back()
        
        edit_delete_view = EditDeletePaymentsView(
            self,
            on_back=self.on_back,
            on_payment_saved=self.on_payment_saved,
            on_navigate_to_dashboard=go_to_dashboard,
            on_register_new_payment=self._show_register_payment,
            on_show_reports=self._show_reports,
        )
        edit_delete_view.pack(fill="both", expand=True)

    def _show_reports(self):
        """Muestra la vista completa de reportes de pagos"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Función para navegar al dashboard principal
        def go_to_dashboard():
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
            # Fallback: usar on_back si está disponible
            if self.on_back:
                self.on_back()
        
        # Importar e instanciar la vista de reportes de pagos
        from manager.app.ui.views.payment_reports_view import PaymentReportsView
        
        reports_view = PaymentReportsView(
            self,
            on_back=self._show_edit_delete_payments,
            on_navigate_to_dashboard=go_to_dashboard
        )
        reports_view.pack(fill="both", expand=True)

    def _on_back(self):
        """Delega en el presenter para volver al dashboard."""
        self.presenter.go_back()

    def _open_new_payment_modal(self):
        # Pasar el inquilino seleccionado en el filtro principal, si existe
        selected_tenant = self.tenant_autocomplete.get_selected_tenant()
        PaymentModal(self, self.tenant_service.get_all_tenants(), on_save=self._on_payment_saved, preselected_tenant=selected_tenant)

    def _open_edit_payment_modal(self, payment):
        PaymentModal(self, self.tenant_service.get_all_tenants(), payment=payment, on_save=self._on_payment_saved)

    def _on_payment_saved(self, _):
        # Solo sonido de confirmación (sin mensaje "Éxito"), según checkpoint Pagos UX
        self.presenter.notify_payment_saved()

    def _confirm_delete_payment(self, payment):
        if messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas eliminar este pago?"):
            success = self.payment_service.delete_payment(payment['id'])
            if success:
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
                self._load_payments()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pago.")

    def _create_payments_list_with_scroll(self):
        # Elimina frames previos si existen
        if hasattr(self, 'list_container'):
            self.list_container.destroy()
        if hasattr(self, 'list_header_frame'):
            self.list_header_frame.destroy()
        cb = self._content_bg
        # Encabezado fijo (no se mueve con el scroll)
        columns = [
            ("Inquilino", 22),
            ("Fecha de pago", 14),
            ("Monto", 14),
            ("Método", 12),
            ("Observaciones", 38)
        ]
        self._table_columns = columns
        header_bg = "#dcfce7"
        header_fg = "#166534"
        self.list_header_frame = tk.Frame(self, bg=header_bg)
        self.list_header_frame.pack(fill="x", padx=2, pady=(0, 0))
        for idx, (col, width) in enumerate(columns):
            tk.Label(
                self.list_header_frame, text=col, font=("Segoe UI", 10, "bold"),
                width=width, anchor="w", bg=header_bg, fg=header_fg
            ).grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
            self.list_header_frame.grid_columnconfigure(idx, weight=1)
        # Contenedor para canvas y scrollbar (solo filas de datos)
        self.list_container = tk.Frame(self, bg=cb)
        self.list_container.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        # Canvas y scrollbar
        self.list_canvas = tk.Canvas(self.list_container, bg=cb, borderwidth=0, highlightthickness=0)
        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=self.list_canvas.yview)
        self.list_scrollbar.pack(side="right", fill="y")
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)
        # Frame interno
        self.list_frame = tk.Frame(self.list_canvas, bg=cb)
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        # Ajustar ancho del frame interno al del canvas
        def _on_canvas_configure(event):
            self.list_canvas.itemconfig(self.list_window, width=event.width)
        self.list_canvas.bind("<Configure>", _on_canvas_configure)
        # Actualizar scrollregion cuando cambie el contenido
        def _on_frame_configure(event):
            self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        self.list_frame.bind("<Configure>", _on_frame_configure)
        # --- Scroll robusto: contador de entradas/salidas ---
        self._scroll_area_hover_count = 0
        def _on_mousewheel(event):
            self.list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_mousewheel(event):
            self._scroll_area_hover_count += 1
            self.list_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            self._scroll_area_hover_count -= 1
            if self._scroll_area_hover_count <= 0:
                self._scroll_area_hover_count = 0
                self.list_canvas.unbind_all("<MouseWheel>")
        self.list_canvas.bind('<Enter>', _bind_mousewheel)
        self.list_canvas.bind('<Leave>', _unbind_mousewheel)
        self.list_frame.bind('<Enter>', _bind_mousewheel)
        self.list_frame.bind('<Leave>', _unbind_mousewheel)

class PaymentModal(tk.Toplevel):
    def __init__(self, parent, tenants, payment=None, on_save=None, preselected_tenant=None, compact=False):
        super().__init__(parent)
        self.title("Registrar Pago" if payment is None else "Editar Pago")
        self.compact = compact
        if compact:
            self.geometry("420x440")
        else:
            self.geometry("400x400")
        self.payment_service = payment_service
        self.payment = payment
        self.on_save = on_save
        self.tenants = tenants
        self.preselected_tenant = preselected_tenant
        self._create_form()
        self._close_modal = self._make_close_modal()
        self.bind_all("<Escape>", self._close_modal)
        self.protocol("WM_DELETE_WINDOW", lambda: self._close_modal(None))
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _make_close_modal(self):
        """Cierra el modal y quita el binding global de Escape (así Esc cierra sin dar foco al modal)."""
        def close(_e=None):
            try:
                self.unbind_all("<Escape>")
            except Exception:
                pass
            self.destroy()
        return close

    def _get_tenant_apartment_display(self, tenant):
        """Texto tipo 'Edificio X - 101' o '—' para el inquilino."""
        if not tenant:
            return "—"
        apt_id = tenant.get("apartamento", None)
        if apt_id is None:
            return "—"
        try:
            apt_id = int(apt_id) if isinstance(apt_id, str) and apt_id.isdigit() else apt_id
            apt = apartment_service.get_apartment_by_id(apt_id)
        except (TypeError, ValueError):
            return "—"
        if not apt:
            return "—"
        building = None
        if hasattr(building_service, "get_building_by_id"):
            building = building_service.get_building_by_id(apt.get("building_id"))
        if not building:
            all_buildings = building_service.get_all_buildings()
            building = next((b for b in all_buildings if b.get("id") == apt.get("building_id")), None)
        building_name = building.get("name", "") if building else ""
        tipo = apt.get("unit_type", "Apartamento Estándar")
        numero = apt.get("number", "")
        if building_name:
            return f"{building_name} - {tipo} {numero}" if tipo != "Apartamento Estándar" else f"{building_name} - {numero}"
        return f"{tipo} {numero}" if tipo != "Apartamento Estándar" else str(numero)

    def _create_form(self):
        pad = (16, 12) if self.compact else (20, 20)
        pady_field = (0, 6) if self.compact else (0, 8)
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=pad[0], pady=pad[1])
        self.vars = {}
        self._form_ready = False  # Flag para evitar callbacks prematuros
        # En modo compacto: primero cuadro de búsqueda + botón Limpiar, luego las 3 líneas de datos (negrita)
        if self.compact:
            tk.Label(frame, text="Cambiar inquilino:", font=("Segoe UI", 9), fg="#666").pack(anchor="w")
            search_row = tk.Frame(frame)
            search_row.pack(fill="x", pady=pady_field)
            self.tenant_autocomplete = TenantAutocompleteEntry(
                search_row, self.tenants, on_select=self._on_tenant_selected, width=32
            )
            self.tenant_autocomplete.pack(side="left", fill="x", expand=True)
            btn_clear_tenant = tk.Button(
                search_row,
                text="Limpiar",
                font=("Segoe UI", 9),
                bg="#e5e7eb",
                fg="#374151",
                relief="flat",
                padx=10,
                pady=4,
                cursor="hand2",
                command=self._clear_tenant_in_modal,
            )
            btn_clear_tenant.pack(side="right", padx=(8, 0))
            btn_clear_tenant.bind("<Enter>", lambda e: btn_clear_tenant.config(bg="#d1d5db"))
            btn_clear_tenant.bind("<Leave>", lambda e: btn_clear_tenant.config(bg="#e5e7eb"))
            tenant_info = tk.Frame(frame)
            tenant_info.pack(fill="x", pady=(4, 6))
            self._lbl_tenant_name = tk.Label(tenant_info, text="Inquilino: —", font=("Segoe UI", 10, "bold"), anchor="w")
            self._lbl_tenant_name.pack(fill="x")
            self._lbl_tenant_id = tk.Label(tenant_info, text="Identificación: —", font=("Segoe UI", 10, "bold"), anchor="w")
            self._lbl_tenant_id.pack(fill="x")
            self._lbl_tenant_apt = tk.Label(tenant_info, text="Apartamento: —", font=("Segoe UI", 10, "bold"), anchor="w")
            self._lbl_tenant_apt.pack(fill="x")
        # Fecha (con mini selector de fecha en modo compacto)
        tk.Label(frame, text="Fecha de pago (DD/MM/YYYY):", font=("Segoe UI", 10)).pack(anchor="w")
        self.fecha_var = tk.StringVar(value=self.payment['fecha_pago'] if self.payment else datetime.now().strftime("%d/%m/%Y"))
        if self.compact:
            date_row = tk.Frame(frame)
            date_row.pack(fill="x", pady=pady_field)
            self.date_picker = DatePickerWidget(date_row)
            self.date_picker.pack(side="left")
            self.date_picker.set(self.fecha_var.get())
            def _on_date_change(_e=None):
                v = self.date_picker.get()
                if v:
                    self.fecha_var.set(v)
            self.date_picker.date_entry.bind("<KeyRelease>", _on_date_change)
            self.date_picker.date_entry.bind("<FocusOut>", _on_date_change)
            _orig_select = self.date_picker._select_date
            _orig_today = self.date_picker._select_today
            def _wrapped_select(day):
                _orig_select(day)
                self.fecha_var.set(self.date_picker.get())
            def _wrapped_today():
                _orig_today()
                self.fecha_var.set(self.date_picker.get())
            self.date_picker._select_date = _wrapped_select
            self.date_picker._select_today = _wrapped_today
        else:
            tk.Entry(frame, textvariable=self.fecha_var, font=("Segoe UI", 10)).pack(fill="x", pady=pady_field)
        # Monto
        tk.Label(frame, text="Monto:", font=("Segoe UI", 10)).pack(anchor="w")
        self.monto_var = tk.StringVar(value=str(self.payment['monto']) if self.payment else "")
        tk.Entry(frame, textvariable=self.monto_var, font=("Segoe UI", 10)).pack(fill="x", pady=pady_field)
        # Método
        tk.Label(frame, text="Método:", font=("Segoe UI", 10)).pack(anchor="w")
        self.metodo_var = tk.StringVar(value=self.payment['metodo'] if self.payment else "Efectivo")
        metodo_combo = ttk.Combobox(frame, textvariable=self.metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=28, font=("Segoe UI", 10))
        metodo_combo.pack(fill="x", pady=pady_field)
        bind_combobox_dropdown_on_click(metodo_combo)
        # Observaciones
        tk.Label(frame, text="Observaciones:", font=("Segoe UI", 10)).pack(anchor="w")
        self.obs_var = tk.StringVar(value=self.payment.get('observaciones', '') if self.payment else "")
        tk.Entry(frame, textvariable=self.obs_var, font=("Segoe UI", 10)).pack(fill="x", pady=pady_field)
        # Inquilino (si no es compacto va al final)
        if not self.compact:
            tk.Label(frame, text="Inquilino:").pack(anchor="w")
            self.tenant_autocomplete = TenantAutocompleteEntry(
                frame, self.tenants, on_select=self._on_tenant_selected, width=30
            )
            self.tenant_autocomplete.pack(fill="x", pady=pady_field)
        self._form_ready = True
        if self.payment:
            for t in self.tenants:
                if t['id'] == self.payment['id_inquilino']:
                    self.tenant_autocomplete._select_tenant(t)
                    break
        elif self.preselected_tenant:
            for t in self.tenants:
                if t['id'] == self.preselected_tenant['id']:
                    self.tenant_autocomplete._select_tenant(t)
                    break
        btn_label = "Registrar Pago" if self.compact else "Guardar"
        btn_save = tk.Button(
            frame,
            text=btn_label,
            command=self._save,
            bg="#22c55e",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        btn_save.pack(pady=(12 if self.compact else 20, 16))
        
        # Hover effect para botón guardar
        def on_enter_save(e):
            btn_save.configure(bg="#16a34a")  # green-600 - verde más oscuro para hover
        def on_leave_save(e):
            btn_save.configure(bg="#22c55e")  # green-500 - verde original
        btn_save.bind("<Enter>", on_enter_save)
        btn_save.bind("<Leave>", on_leave_save)

    def _clear_tenant_in_modal(self):
        """Limpia la selección de inquilino para poder buscar otro sin borrar el texto a mano."""
        if not self.compact or not hasattr(self, "tenant_autocomplete"):
            return
        self.tenant_autocomplete.clear_selection()
        self.selected_tenant = None
        if hasattr(self, "_lbl_tenant_name"):
            self._lbl_tenant_name.configure(text="Inquilino: —")
            self._lbl_tenant_id.configure(text="Identificación: —")
            self._lbl_tenant_apt.configure(text="Apartamento: —")
        self.monto_var.set("")

    def _on_tenant_selected(self, tenant):
        if not hasattr(self, '_form_ready') or not self._form_ready:
            return
        self.selected_tenant = tenant
        # En modo compacto, actualizar las 3 líneas de datos del inquilino
        if self.compact and hasattr(self, '_lbl_tenant_name'):
            if tenant:
                self._lbl_tenant_name.configure(text=f"Inquilino: {tenant.get('nombre', '') or '—'}")
                self._lbl_tenant_id.configure(text=f"Identificación: {tenant.get('numero_documento', '') or '—'}")
                self._lbl_tenant_apt.configure(text=f"Apartamento: {self._get_tenant_apartment_display(tenant)}")
            else:
                self._lbl_tenant_name.configure(text="Inquilino: —")
                self._lbl_tenant_id.configure(text="Identificación: —")
                self._lbl_tenant_apt.configure(text="Apartamento: —")
        # Autocompletar el monto con el valor del arriendo solo si:
        # - Es un nuevo pago (no edición)
        # - O el campo monto está vacío
        if (not hasattr(self, 'payment') or not self.payment) or not self.monto_var.get().strip():
            valor_arriendo = tenant.get('valor_arriendo', '') if tenant else ''
            self.monto_var.set(str(valor_arriendo) if valor_arriendo else '')

    def _save(self):
        # Validaciones
        tenant = self.tenant_autocomplete.get_selected_tenant()
        if not tenant:
            messagebox.showerror("Error", "Debe seleccionar un inquilino.")
            return
        fecha_str = (self.date_picker.get() if (self.compact and hasattr(self, "date_picker") and self.date_picker.winfo_exists()) else None) or self.fecha_var.get()
        if not fecha_str:
            messagebox.showerror("Error", "Debe ingresar la fecha de pago.")
            return
        try:
            datetime.strptime(fecha_str, "%d/%m/%Y")
        except Exception:
            messagebox.showerror("Error", "La fecha debe tener formato DD/MM/YYYY.")
            return
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return
        data = {
            "id_inquilino": tenant['id'],
            "nombre_inquilino": tenant['nombre'],
            "fecha_pago": fecha_str,
            "monto": float(self.monto_var.get()),
            "metodo": self.metodo_var.get(),
            "observaciones": self.obs_var.get()
        }
        # Evitar duplicados (misma fecha y monto para el mismo inquilino)
        if not self.payment:
            existing = self.payment_service.get_payments_by_tenant(tenant['id'])
            for p in existing:
                if p.get('fecha_pago') == data['fecha_pago'] and p.get('monto') == data['monto']:
                    messagebox.showwarning("Advertencia", "Ya existe un pago con la misma fecha y monto para este inquilino.")
                    return
        if self.payment:
            self.payment_service.update_payment(self.payment['id'], data)
        else:
            self.payment_service.add_payment(data)
        # Solo sonido de confirmación (mismo que el del cuadro de éxito), sin mensaje
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        if self.on_save:
            self.on_save(data)
        self.destroy()

class PaymentsManagerWindow(tk.Toplevel):
    def __init__(self, parent, tenant_service, payment_service):
        super().__init__(parent)
        self.title("Gestión de Pagos")
        self.geometry("700x600")
        self.tenant_service = tenant_service
        self.payment_service = payment_service
        self.selected_tenant = None
        self._build_ui()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _build_ui(self):
        # Sección superior: búsqueda de inquilino
        top_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(top_frame, text="Buscar inquilino:", **theme_manager.get_style("label_body")).pack(anchor="w")
        self.tenants = self.tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            top_frame,
            self.tenants,
            on_select=self._on_tenant_selected,
            width=50
        )
        self.tenant_autocomplete.pack(fill="x", pady=(0, 8))

        # Sección central: formulario de pago
        self.form_frame = tk.Frame(self, **theme_manager.get_style("card"))
        self.form_frame.pack(fill="x", padx=20, pady=(0, 10))
        self._build_payment_form()

        # Sección inferior: listado de pagos
        self.list_frame = tk.Frame(self, **theme_manager.get_style("card"))
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._display_payments([])

    def _build_payment_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.fecha_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.monto_var = tk.StringVar()
        self.metodo_var = tk.StringVar(value="Efectivo")
        self.obs_var = tk.StringVar()
        # Fecha
        tk.Label(self.form_frame, text="Fecha de pago (DD/MM/YYYY):").pack(anchor="w")
        tk.Entry(self.form_frame, textvariable=self.fecha_var).pack(fill="x", pady=(0, 6))
        # Monto
        tk.Label(self.form_frame, text="Monto:").pack(anchor="w")
        tk.Entry(self.form_frame, textvariable=self.monto_var).pack(fill="x", pady=(0, 6))
        # Método
        tk.Label(self.form_frame, text="Método:").pack(anchor="w")
        metodo_combo = ttk.Combobox(self.form_frame, textvariable=self.metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=20)
        metodo_combo.pack(fill="x", pady=(0, 6))
        bind_combobox_dropdown_on_click(metodo_combo)
        # Observaciones
        tk.Label(self.form_frame, text="Observaciones:").pack(anchor="w")
        tk.Entry(self.form_frame, textvariable=self.obs_var).pack(fill="x", pady=(0, 6))
        # Botón guardar - Verde para mantener tonalidad verde del módulo
        btn_save = tk.Button(
            self.form_frame, 
            text="Registrar Pago", 
            command=self._save_payment,
            bg="#22c55e",  # green-500 - verde para mantener tonalidad verde del módulo
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        btn_save.pack(pady=(10, 0))
        
        # Hover effect para botón registrar
        def on_enter_save(e):
            btn_save.configure(bg="#16a34a")  # green-600 - verde más oscuro para hover
        def on_leave_save(e):
            btn_save.configure(bg="#22c55e")  # green-500 - verde original
        btn_save.bind("<Enter>", on_enter_save)
        btn_save.bind("<Leave>", on_leave_save)

    def _on_tenant_selected(self, tenant):
        self.selected_tenant = tenant
        # Autocompletar monto
        self.monto_var.set(str(tenant.get('valor_arriendo', '')))
        # Mostrar pagos del inquilino
        payments = [p for p in self.payment_service.get_all_payments() if p['id_inquilino'] == tenant['id']]
        self._display_payments(payments)

    def _display_payments(self, payments):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        if not payments:
            tk.Label(self.list_frame, text="No hay pagos registrados para este inquilino.", font=("Segoe UI", 11), fg="#666").pack(pady=20)
            return
        for payment in payments:
            card = ModernCard(self.list_frame)
            card.pack(fill="x", pady=(0, Spacing.SM), padx=(0, 0))
            info = tk.Frame(card.content_frame, **theme_manager.get_style("frame"))
            info.pack(fill="x")
            # Mostrar nombre y apartamento
            nombre = payment.get('nombre_inquilino', '')
            apto = ''
            # Buscar apartamento real del inquilino
            for t in self.tenants:
                if t['id'] == payment['id_inquilino']:
                    apt_id = t.get('apartamento', '')
                    if apt_id:
                        try:
                            apt = apartment_service.get_apartment_by_id(int(apt_id))
                            if apt and 'number' in apt:
                                apto = apt['number']
                            else:
                                apto = apt_id
                        except Exception:
                            apto = apt_id
                    break
            tk.Label(info, text=f"{nombre} (Apt. {apto})", font=("Segoe UI", 11, "bold"), fg="#222").pack(side="left", padx=(0, Spacing.LG))
            tk.Label(info, text=f"{payment['fecha_pago']}", font=("Segoe UI", 10), fg="#1976d2").pack(side="left")
            tk.Label(info, text=f"Monto: ${payment['monto']:,.2f}", font=("Segoe UI", 10)).pack(side="left", padx=(Spacing.LG, 0))
            tk.Label(info, text=f"Método: {payment['metodo']}", font=("Segoe UI", 10)).pack(side="left", padx=(Spacing.LG, 0))
            tk.Label(info, text=f"Obs: {payment.get('observaciones','')}", font=("Segoe UI", 10)).pack(side="left", padx=(Spacing.LG, 0))
            # Aquí puedes agregar botones de editar/eliminar si lo deseas

    def _save_payment(self):
        if not self.selected_tenant:
            messagebox.showerror("Error", "Debe seleccionar un inquilino.")
            return
        if not self.fecha_var.get():
            messagebox.showerror("Error", "Debe ingresar la fecha de pago.")
            return
        try:
            datetime.strptime(self.fecha_var.get(), "%d/%m/%Y")
        except Exception:
            messagebox.showerror("Error", "La fecha debe tener formato DD/MM/YYYY.")
            return
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return
        data = {
            "id_inquilino": self.selected_tenant['id'],
            "nombre_inquilino": self.selected_tenant['nombre'],
            "fecha_pago": self.fecha_var.get(),
            "monto": float(self.monto_var.get()),
            "metodo": self.metodo_var.get(),
            "observaciones": self.obs_var.get()
        }
        self.payment_service.add_payment(data)
        messagebox.showinfo("Éxito", "Pago registrado correctamente.")
        # Refrescar lista de pagos
        payments = [p for p in self.payment_service.get_all_payments() if p['id_inquilino'] == self.selected_tenant['id']]
        self._display_payments(payments)
        # Limpiar formulario
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.monto_var.set(str(self.selected_tenant.get('valor_arriendo', '')))
        self.metodo_var.set("Efectivo")
        self.obs_var.set("") 