import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard, ModernSeparator
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.payment_service import PaymentService
from manager.app.services.tenant_service import TenantService
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from .edit_delete_payments_view import EditDeletePaymentsView
from manager.app.services.apartment_service import apartment_service

class PaymentsView(tk.Frame):
    """Vista profesional para gestión de pagos de inquilinos"""
    def __init__(self, parent, on_back=None, preselected_tenant=None, on_payment_saved=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        self.on_back = on_back
        self.preselected_tenant = preselected_tenant
        self.on_payment_saved = on_payment_saved  # Callback para actualizar otras vistas
        self._create_layout()
        # self._load_payments()  # Eliminado: solo se usará en la funcionalidad específica

    def _create_layout(self):
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG))
        btn_back = ModernButton(header, text="Volver", icon=Icons.ARROW_LEFT, style="secondary", command=self._on_back)
        btn_back.pack(side="left")
        title = tk.Label(header, text="Gestión de Pagos", **theme_manager.get_style("label_title"))
        title.pack(side="left", padx=(Spacing.LG, 0))
        # Cards principales
        cards_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        cards_frame.pack(pady=Spacing.XL)
        self._create_action_card(
            cards_frame,
            icon=Icons.PAYMENT_RECEIVED,
            title="Registrar nuevo pago",
            description="Registra un nuevo pago de arriendo para cualquier inquilino.",
            color="#1976d2",
            command=self._show_register_payment
        ).pack(side="left", padx=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.EDIT,
            title="Editar/Eliminar pago",
            description="Consulta, edita o elimina pagos registrados previamente.",
            color="#388e3c",
            command=self._show_edit_delete_payments
        ).pack(side="left", padx=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.REPORTS,
            title="Reportes",
            description="Visualiza reportes y estadísticas de pagos.",
            color="#fbc02d",
            command=self._show_reports
        ).pack(side="left", padx=Spacing.LG)

    def _create_action_card(self, parent, icon, title, description, color, command):
        card = tk.Frame(parent, bg="white", bd=2, relief="raised", padx=18, pady=18, width=260, height=220)
        card.pack_propagate(False)  # Mantener tamaño fijo
        card.bind("<Button-1>", lambda e: command())
        card.configure(cursor="hand2")
        # Ícono
        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 28), fg=color, bg="white")
        icon_label.pack()
        # Título
        title_label = tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), fg=color, bg="white")
        title_label.pack(pady=(8, 2))
        # Descripción
        desc_label = tk.Label(card, text=description, font=("Segoe UI", 10), fg="#444", bg="white", wraplength=200, justify="center")
        desc_label.pack(pady=(0, 2))
        # Hover effect
        def on_enter(e):
            card.configure(bg="#e3f2fd")
            icon_label.configure(bg="#e3f2fd")
            title_label.configure(bg="#e3f2fd")
            desc_label.configure(bg="#e3f2fd")
        def on_leave(e):
            card.configure(bg="white")
            icon_label.configure(bg="white")
            title_label.configure(bg="white")
            desc_label.configure(bg="white")
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for w in [icon_label, title_label, desc_label]:
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.configure(cursor="hand2")
        return card

    def _show_register_payment(self, preselected_tenant=None):
        # Cambiar el título global de la ventana
        try:
            self.master.master.page_title.configure(text="Registrar pagos")
        except Exception:
            pass
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        # Header con búsqueda y botón volver en la misma línea
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, 10), padx=(2, 2))
        # Frame izquierdo: búsqueda y limpiar
        left_header = tk.Frame(header, **theme_manager.get_style("frame"))
        left_header.pack(side="left", fill="x", expand=True)
        label_style = theme_manager.get_style("label_body").copy()
        label_style["font"] = ("Segoe UI", 14, "bold")
        tk.Label(left_header, text="Buscar inquilino:", **label_style).pack(side="left")
        self.tenants = self.tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            left_header,
            self.tenants,
            on_select=self._on_register_tenant_selected,
            width=70
        )
        self.tenant_autocomplete.pack(side="left", padx=(2, 0))
        btn_clear = ModernButton(left_header, text="Limpiar búsqueda", icon=Icons.CANCEL, style="warning", command=self._clear_tenant_search, small=True)
        btn_clear.pack(side="left", padx=(2, 0))
        # Frame derecho: botón volver
        btn_back = ModernButton(header, text="Volver", icon=Icons.ARROW_LEFT, style="secondary", command=self._restore_global_title)
        btn_back.pack(side="right", pady=(0, 0))
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
        # Sección central: formulario de pago (padding mínimo)
        self.form_frame = tk.Frame(self, **theme_manager.get_style("card"))
        self.form_frame.pack(fill="x", padx=2, pady=(0, 2))
        self._build_register_payment_form()
        # Sección inferior: listado de pagos con scroll profesional
        self._create_payments_list_with_scroll()
        # Si hay un inquilino preseleccionado, autocompletar el campo
        if self.selected_tenant:
            self.tenant_autocomplete._select_tenant(self.selected_tenant)
        self._display_register_payments(self._get_all_payments())

    def _restore_global_title(self):
        try:
            self.master.master.page_title.configure(text="Control de Pagos")
        except Exception:
            pass
        self._create_layout()

    def _build_register_payment_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        row_opts = {'padx': (0, 8), 'pady': 2}
        # Fecha
        row1 = tk.Frame(self.form_frame, **theme_manager.get_style("frame"))
        row1.pack(fill="x", pady=1)
        tk.Label(row1, text="Fecha de pago (DD/MM/YYYY):", width=22, anchor="w").pack(side="left", **row_opts)
        tk.Entry(row1, textvariable=self.fecha_var, width=18).pack(side="left", **row_opts)
        # Monto
        row2 = tk.Frame(self.form_frame, **theme_manager.get_style("frame"))
        row2.pack(fill="x", pady=1)
        tk.Label(row2, text="Monto:", width=22, anchor="w").pack(side="left", **row_opts)
        tk.Entry(row2, textvariable=self.monto_var, width=18).pack(side="left", **row_opts)
        # Método
        row3 = tk.Frame(self.form_frame, **theme_manager.get_style("frame"))
        row3.pack(fill="x", pady=1)
        tk.Label(row3, text="Método:", width=22, anchor="w").pack(side="left", **row_opts)
        metodo_combo = ttk.Combobox(row3, textvariable=self.metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=16)
        metodo_combo.pack(side="left", **row_opts)
        # Observaciones
        row4 = tk.Frame(self.form_frame, **theme_manager.get_style("frame"))
        row4.pack(fill="x", pady=1)
        tk.Label(row4, text="Observaciones:", width=22, anchor="w").pack(side="left", **row_opts)
        tk.Entry(row4, textvariable=self.obs_var, width=40).pack(side="left", **row_opts)
        # Botón guardar alineado a la IZQUIERDA
        btn_save = tk.Button(self.form_frame, text="Registrar Pago", command=self._save_register_payment)
        btn_save.pack(pady=(4, 0), anchor="w")

    def _clear_tenant_search(self):
        self.tenant_autocomplete.set_tenants(self.tenants)
        self.selected_tenant = None
        self.monto_var.set("")
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.metodo_var.set("Efectivo")
        self.obs_var.set("")
        self._display_register_payments(self._get_all_payments())

    def _get_all_payments(self):
        pagos = self.payment_service.get_all_payments()
        # Mostrar el último pago registrado primero (orden de registro, no por fecha)
        return list(reversed(pagos))

    def _on_register_tenant_selected(self, tenant):
        self.selected_tenant = tenant
        if hasattr(self, 'monto_var'):
            self.monto_var.set(str(tenant.get('valor_arriendo', '')))
        pagos = [p for p in self._get_all_payments() if p['id_inquilino'] == tenant['id']]
        # Ya vienen ordenados por fecha descendente desde _get_all_payments
        self._display_register_payments(pagos)

    def _display_register_payments(self, payments):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        # Frame de tabla (encabezado + filas)
        table_frame = tk.Frame(self.list_frame, **theme_manager.get_style("frame"))
        table_frame.pack(fill="x", pady=(0, 2))
        columns = [
            ("Inquilino", 22),
            ("Fecha de pago", 14),
            ("Monto", 14),
            ("Método", 12),
            ("Observaciones", 38)
        ]
        # Encabezado
        for idx, (col, width) in enumerate(columns):
            tk.Label(table_frame, text=col, font=("Segoe UI", 10, "bold"), width=width, anchor="w", bg="#f5f5f5").grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
            table_frame.grid_columnconfigure(idx, weight=1)
        if not payments:
            tk.Label(table_frame, text="No hay pagos registrados.", font=("Segoe UI", 11), fg="#666").grid(row=1, column=0, columnspan=len(columns), pady=10, sticky="w")
            return
        zebra_colors = ("#ffffff", "#f0f4fa")
        for row_idx, payment in enumerate(payments, start=1):
            bg_color = zebra_colors[row_idx % 2]
            # Frame de fondo para toda la fila
            row_bg = tk.Frame(table_frame, bg=bg_color)
            row_bg.grid(row=row_idx, column=0, columnspan=len(columns), sticky="nsew")
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
        
        self._display_register_payments(self._get_all_payments())
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.monto_var.set(str(self.selected_tenant.get('valor_arriendo', '')))
        self.metodo_var.set("Efectivo")
        self.obs_var.set("")

    def _generate_payment_receipt_pdf(self, pago):
        import os
        folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../recibos'))
        os.makedirs(folder, exist_ok=True)
        nombre = pago.get("nombre_inquilino", "Inquilino").replace(" ", "_")
        fecha = pago.get("fecha_pago", "").replace("/", "-")
        filename = f"recibo_pago_{nombre}_{fecha}.pdf"
        filepath = os.path.join(folder, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        # Logo placeholder
        c.setFillColorRGB(0.2, 0.4, 0.7)
        c.rect(40, height-80, 80, 40, fill=1)
        c.setFillColorRGB(1,1,1)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height-60, "LOGO")
        # Encabezado
        c.setFillColorRGB(0,0,0)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(140, height-60, "RECIBO DE PAGO DE ARRENDAMIENTO")
        c.setFont("Helvetica", 10)
        c.drawString(140, height-80, f"Emitido: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        # Datos del inquilino y pago
        y = height-120
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Datos del Inquilino:")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Nombre: {pago.get('nombre_inquilino', '')}")
        y -= 15
        c.drawString(50, y, f"Apartamento: {self.selected_tenant.get('apartamento', '')}")
        y -= 15
        c.drawString(50, y, f"Documento: {self.selected_tenant.get('numero_documento', '')}")
        y -= 25
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Detalles del Pago:")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Fecha de pago: {pago.get('fecha_pago', '')}")
        y -= 15
        c.drawString(50, y, f"Monto: ${pago.get('monto', 0):,.2f}")
        y -= 15
        c.drawString(50, y, f"Método: {pago.get('metodo', '')}")
        y -= 15
        c.drawString(50, y, f"Observaciones: {pago.get('observaciones', '')}")
        y -= 30
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(40, y, "Este recibo certifica que el inquilino ha realizado el pago correspondiente al arriendo en la fecha indicada.")
        y -= 40
        c.setFont("Helvetica", 10)
        c.drawString(40, y, "Firma administrador: _____________________________")
        c.drawString(320, y, "Firma inquilino: _____________________________")
        c.save()
        return filepath

    def _show_edit_delete_payments(self):
        from .edit_delete_payments_view import EditDeletePaymentsView
        # Limpiar vista y mostrar la vista profesional de edición/eliminación de pagos
        for widget in self.winfo_children():
            widget.destroy()
        edit_delete_view = EditDeletePaymentsView(
            self, 
            on_back=self._create_layout,
            on_payment_saved=self.on_payment_saved
        )
        edit_delete_view.pack(fill="both", expand=True)

    def _show_reports(self):
        messagebox.showinfo("Reportes de Pagos", "Aquí se mostrarán los reportes y estadísticas de pagos.")

    def _on_back(self):
        if self.on_back:
            self.on_back()

    def _open_new_payment_modal(self):
        # Pasar el inquilino seleccionado en el filtro principal, si existe
        selected_tenant = self.tenant_autocomplete.get_selected_tenant()
        PaymentModal(self, self.tenant_service.get_all_tenants(), on_save=self._on_payment_saved, preselected_tenant=selected_tenant)

    def _open_edit_payment_modal(self, payment):
        PaymentModal(self, self.tenant_service.get_all_tenants(), payment=payment, on_save=self._on_payment_saved)

    def _on_payment_saved(self, _):
        messagebox.showinfo("Éxito", "Pago registrado correctamente.")
        # Aquí podrías recargar la lista de pagos o refrescar la vista si lo deseas en el futuro

    def _confirm_delete_payment(self, payment):
        if messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas eliminar este pago?"):
            success = self.payment_service.delete_payment(payment['id'])
            if success:
                self._load_payments()
                messagebox.showinfo("Eliminado", "Pago eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el pago.")

    def _create_payments_list_with_scroll(self):
        # Elimina frames previos si existen
        if hasattr(self, 'list_container'):
            self.list_container.destroy()
        # Contenedor para canvas y scrollbar
        self.list_container = tk.Frame(self, **theme_manager.get_style("card"))
        self.list_container.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        # Canvas y scrollbar
        self.list_canvas = tk.Canvas(self.list_container, borderwidth=0, highlightthickness=0)
        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_scrollbar = tk.Scrollbar(self.list_container, orient="vertical", command=self.list_canvas.yview)
        self.list_scrollbar.pack(side="right", fill="y")
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)
        # Frame interno
        self.list_frame = tk.Frame(self.list_canvas, **theme_manager.get_style("card"))
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
    def __init__(self, parent, tenants, payment=None, on_save=None, preselected_tenant=None):
        super().__init__(parent)
        self.title("Registrar Pago" if payment is None else "Editar Pago")
        self.geometry("400x400")
        self.payment_service = PaymentService()
        self.payment = payment
        self.on_save = on_save
        self.tenants = tenants
        self.preselected_tenant = preselected_tenant
        self._create_form()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _create_form(self):
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.vars = {}
        self._form_ready = False  # Flag para evitar callbacks prematuros
        # Fecha
        tk.Label(frame, text="Fecha de pago (DD/MM/YYYY):").pack(anchor="w")
        self.fecha_var = tk.StringVar(value=self.payment['fecha_pago'] if self.payment else datetime.now().strftime("%d/%m/%Y"))
        tk.Entry(frame, textvariable=self.fecha_var).pack(fill="x", pady=(0, 8))
        # Monto
        tk.Label(frame, text="Monto:").pack(anchor="w")
        self.monto_var = tk.StringVar(value=str(self.payment['monto']) if self.payment else "")
        tk.Entry(frame, textvariable=self.monto_var).pack(fill="x", pady=(0, 8))
        # Método
        tk.Label(frame, text="Método:").pack(anchor="w")
        self.metodo_var = tk.StringVar(value=self.payment['metodo'] if self.payment else "Efectivo")
        metodo_combo = ttk.Combobox(frame, textvariable=self.metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=20)
        metodo_combo.pack(fill="x", pady=(0, 8))
        # Observaciones
        tk.Label(frame, text="Observaciones:").pack(anchor="w")
        self.obs_var = tk.StringVar(value=self.payment.get('observaciones', '') if self.payment else "")
        tk.Entry(frame, textvariable=self.obs_var).pack(fill="x", pady=(0, 8))
        # Inquilino (autocomplete al final para que los campos ya existan)
        tk.Label(frame, text="Inquilino:").pack(anchor="w")
        self.tenant_autocomplete = TenantAutocompleteEntry(
            frame,
            self.tenants,
            on_select=self._on_tenant_selected,
            width=30
        )
        self.tenant_autocomplete.pack(fill="x", pady=(0, 8))
        self._form_ready = True  # Ahora sí se pueden autocompletar campos
        # Seleccionar automáticamente el inquilino si viene preseleccionado
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
        # Botón guardar
        btn_save = tk.Button(frame, text="Guardar", command=self._save)
        btn_save.pack(pady=(20, 0))

    def _on_tenant_selected(self, tenant):
        if not hasattr(self, '_form_ready') or not self._form_ready:
            return
        self.selected_tenant = tenant
        # Autocompletar el monto con el valor del arriendo solo si:
        # - Es un nuevo pago (no edición)
        # - O el campo monto está vacío
        if (not hasattr(self, 'payment') or not self.payment) or not self.monto_var.get().strip():
            valor_arriendo = tenant.get('valor_arriendo', '')
            self.monto_var.set(str(valor_arriendo) if valor_arriendo else '')

    def _save(self):
        # Validaciones
        tenant = self.tenant_autocomplete.get_selected_tenant()
        if not tenant:
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
            "id_inquilino": tenant['id'],
            "nombre_inquilino": tenant['nombre'],
            "fecha_pago": self.fecha_var.get(),
            "monto": float(self.monto_var.get()),
            "metodo": self.metodo_var.get(),
            "observaciones": self.obs_var.get()
        }
        if self.payment:
            self.payment_service.update_payment(self.payment['id'], data)
        else:
            self.payment_service.add_payment(data)
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
        # Observaciones
        tk.Label(self.form_frame, text="Observaciones:").pack(anchor="w")
        tk.Entry(self.form_frame, textvariable=self.obs_var).pack(fill="x", pady=(0, 6))
        # Botón guardar
        btn_save = tk.Button(self.form_frame, text="Registrar Pago", command=self._save_payment)
        btn_save.pack(pady=(10, 0))

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