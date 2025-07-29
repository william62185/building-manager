import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.payment_service import PaymentService
from manager.app.services.tenant_service import TenantService

class EditDeletePaymentsView(tk.Frame):
    """Vista profesional para editar/eliminar pagos (independiente, duplicado de registrar pago)"""
    def __init__(self, parent, on_back=None, on_payment_saved=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        self.on_back = on_back
        self.on_payment_saved = on_payment_saved  # Callback para actualizar otras vistas
        self.selected_tenant = None
        self.editing_payment = None
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG))
        btn_back = ModernButton(header, text="Volver", icon=Icons.ARROW_LEFT, style="secondary", command=self._on_back)
        btn_back.pack(side="left")
        title = tk.Label(header, text="Editar/Eliminar Pagos", **theme_manager.get_style("label_title"))
        title.pack(side="left", padx=(Spacing.LG, 0))
        # Buscador de inquilino
        search_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        search_frame.pack(fill="x", pady=(0, 10), padx=(2, 2))
        label_style = theme_manager.get_style("label_body").copy()
        label_style["font"] = ("Segoe UI", 14, "bold")
        tk.Label(search_frame, text="Buscar inquilino:", **label_style).pack(side="left")
        self.tenants = self.tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            search_frame,
            self.tenants,
            on_select=self._on_tenant_selected,
            width=70
        )
        self.tenant_autocomplete.pack(side="left", padx=(2, 0))
        btn_clear = ModernButton(search_frame, text="Limpiar búsqueda", icon=Icons.CANCEL, style="warning", command=self._clear_tenant_search, small=True)
        btn_clear.pack(side="left", padx=(2, 0))
        # Contenedor fijo para el formulario de edición
        self.edit_placeholder = tk.Frame(self, **theme_manager.get_style("card"))
        self.edit_placeholder.pack(fill="x", padx=2, pady=(4, 8))
        # Separador visual fino
        separator = tk.Frame(self, height=2, bg="#e0e0e0")
        separator.pack(fill="x", padx=2, pady=(0, 0))
        # Listado profesional de pagos
        self._create_payments_list()

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
        # --- SCROLL PROFESIONAL ---
        self.list_container = tk.Frame(self, **theme_manager.get_style("card"))
        self.list_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        canvas = tk.Canvas(self.list_container, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Frame interno para el contenido
        content_frame = tk.Frame(canvas, **theme_manager.get_style("card"))
        list_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content_frame.bind("<Configure>", _on_frame_configure)
        def _on_canvas_configure(event):
            canvas.itemconfig(list_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        # --- SCROLL CON MOUSE ---
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
        # --- CONTENIDO DEL LISTADO ---
        pagos = self.payment_service.get_all_payments()
        if self.selected_tenant:
            pagos = [p for p in pagos if p['id_inquilino'] == self.selected_tenant['id']]
        pagos = list(reversed(pagos))  # Mostrar el último pago primero
        columns = [
            ("Inquilino", 22),
            ("Fecha de pago", 14),
            ("Monto", 14),
            ("Método", 12),
            ("Observaciones", 38),
            ("Acciones", 12)
        ]
        # Encabezado
        header = tk.Frame(content_frame, bg="#f5f5f5")
        header.grid(row=0, column=0, sticky="ew")
        for idx, (col, width) in enumerate(columns):
            tk.Label(header, text=col, font=("Segoe UI", 10, "bold"), width=width, anchor="w", bg="#f5f5f5").grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
            header.grid_columnconfigure(idx, weight=1)
        # Filas
        zebra_colors = ("#ffffff", "#f0f4fa")
        for row_idx, payment in enumerate(pagos, start=1):
            bg_color = zebra_colors[row_idx % 2]
            row = tk.Frame(content_frame, bg=bg_color)
            row.grid(row=row_idx, column=0, sticky="ew")
            nombre = payment.get('nombre_inquilino', '')
            apto = ''
            for t in self.tenants:
                if t['id'] == payment['id_inquilino']:
                    apto = t.get('apartamento', '')
                    break
            values = [
                f"{nombre} (Apt. {apto})",
                f"{payment['fecha_pago']}",
                f"${payment['monto']:,.2f}",
                f"{payment['metodo']}",
                f"{payment.get('observaciones','')}"
            ]
            for col_idx, (val, (_, width)) in enumerate(zip(values, columns)):
                tk.Label(row, text=val, font=("Segoe UI", 10), width=width, anchor="w", bg=bg_color).grid(row=0, column=col_idx, padx=(0, 1), sticky="nsew")
                row.grid_columnconfigure(col_idx, weight=1)
            # Acciones: iconos editar y eliminar
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
        # Asegurarse de que el contenedor esté empacado justo después del buscador
        if not self.edit_placeholder.winfo_ismapped():
            self.edit_placeholder.pack_forget()
            self.edit_placeholder.pack(after=self.winfo_children()[1], fill="x", padx=2, pady=(4, 8))
        self._build_edit_payment_form()

    def _build_edit_payment_form(self):
        # Destruir cualquier formulario anterior
        for widget in self.edit_placeholder.winfo_children():
            widget.destroy()
        row_opts = {'padx': (0, 8), 'pady': 2}
        # Fecha
        row1 = tk.Frame(self.edit_placeholder, **theme_manager.get_style("frame"))
        row1.pack(fill="x", pady=1)
        tk.Label(row1, text="Fecha de pago (DD/MM/YYYY):", width=22, anchor="w").pack(side="left", **row_opts)
        fecha_var = tk.StringVar(value=self.editing_payment['fecha_pago'])
        tk.Entry(row1, textvariable=fecha_var, width=18).pack(side="left", **row_opts)
        # Monto
        row2 = tk.Frame(self.edit_placeholder, **theme_manager.get_style("frame"))
        row2.pack(fill="x", pady=1)
        tk.Label(row2, text="Monto:", width=22, anchor="w").pack(side="left", **row_opts)
        monto_var = tk.StringVar(value=str(self.editing_payment['monto']))
        tk.Entry(row2, textvariable=monto_var, width=18).pack(side="left", **row_opts)
        # Método
        row3 = tk.Frame(self.edit_placeholder, **theme_manager.get_style("frame"))
        row3.pack(fill="x", pady=1)
        tk.Label(row3, text="Método:", width=22, anchor="w").pack(side="left", **row_opts)
        metodo_var = tk.StringVar(value=self.editing_payment['metodo'])
        metodo_combo = ttk.Combobox(row3, textvariable=metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=16)
        metodo_combo.pack(side="left", **row_opts)
        # Observaciones
        row4 = tk.Frame(self.edit_placeholder, **theme_manager.get_style("frame"))
        row4.pack(fill="x", pady=1)
        tk.Label(row4, text="Observaciones:", width=22, anchor="w").pack(side="left", **row_opts)
        obs_var = tk.StringVar(value=self.editing_payment.get('observaciones', ''))
        tk.Entry(row4, textvariable=obs_var, width=40).pack(side="left", **row_opts)
        # Botones guardar/cancelar
        btns = tk.Frame(self.edit_placeholder, **theme_manager.get_style("frame"))
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

    def _on_back(self):
        if self.on_back:
            self.on_back() 