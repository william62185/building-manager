import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
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
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
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
        self.configure(bg=self._content_bg)
        bg_view = self._content_bg
        # Header
        header = tk.Frame(self, bg=bg_view)
        header.pack(fill="x", pady=(0, Spacing.LG))
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, bg=bg_view)
        buttons_frame.pack(side="right")
        
        # Agregar solo botón Dashboard (sin Volver porque es redundante)
        self._create_navigation_buttons(buttons_frame, self._on_back, show_back_button=False)
        
        # Pregunta principal
        theme = theme_manager.themes[theme_manager.current_theme]
        question_label = tk.Label(
            self,
            text="¿Qué deseas hacer?",
            font=("Segoe UI", 14),
            fg=theme["text_primary"],
            bg=bg_view
        )
        question_label.pack(pady=(0, Spacing.XL))
        
        # Cards principales (fondo igual al de la vista para que se vea transparente)
        cards_frame = tk.Frame(self, bg=bg_view)
        cards_frame.pack(pady=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.PAYMENT_RECEIVED,
            title="Registrar nuevo pago",
            description="Registra un nuevo pago de arriendo para cualquier inquilino.",
            color="#166534",  # verde oscuro - paleta verde armoniosa
            command=self._show_register_payment
        ).pack(side="left", padx=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.EDIT,
            title="Editar/Eliminar pago",
            description="Consulta, edita o elimina pagos registrados previamente.",
            color="#166534",  # mismo color que Registrar nuevo pago para consistencia
            command=self._show_edit_delete_payments
        ).pack(side="left", padx=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.REPORTS,
            title="Reportes",
            description="Visualiza reportes y estadísticas de pagos.",
            color="#166534",  # mismo color que Registrar nuevo pago para consistencia
            command=self._show_reports
        ).pack(side="left", padx=Spacing.LG)

    def _create_action_card(self, parent, icon, title, description, color, command):
        """Crea una card de acción con hover effects - mismo estilo que módulo inquilinos"""
        # Color verde más intenso para el fondo base de las tarjetas (similar al hover anterior)
        light_green_bg = "#dcfce7"  # green-100 - verde claro más intenso para mejor contraste con iconos verdes
        
        card = tk.Frame(parent, bg=light_green_bg, bd=2, relief="raised", width=260, height=220)
        card.pack_propagate(False)  # Mantener tamaño fijo
        
        # Contenedor principal con padding uniforme para centrar verticalmente
        content_frame = tk.Frame(card, bg=light_green_bg)
        content_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Frame espaciador superior para centrar el contenido
        top_spacer = tk.Frame(content_frame, bg=light_green_bg, height=1)
        top_spacer.pack(fill="x", expand=True)
        
        # Contenedor del contenido (icono, título)
        content_container = tk.Frame(content_frame, bg=light_green_bg)
        content_container.pack()
        
        # Ícono
        icon_label = tk.Label(content_container, text=icon, font=("Segoe UI", 28), fg=color, bg=light_green_bg)
        icon_label.pack(pady=(0, Spacing.MD))
        
        # Título
        title_label = tk.Label(content_container, text=title, font=("Segoe UI", 14, "bold"), fg="#000000", bg=light_green_bg)
        title_label.pack()
        
        # Textos descriptivos eliminados según solicitud del usuario
        
        # Frame espaciador inferior para centrar el contenido
        bottom_spacer = tk.Frame(content_frame, bg=light_green_bg, height=1)
        bottom_spacer.pack(fill="x", expand=True)
        
        # Función para manejar clics - se ejecuta desde cualquier parte del card
        def on_card_click(e):
            # Prevenir propagación adicional si es necesario
            e.widget.focus_set()  # Asegurar que el widget tenga foco
            command()
            return "break"  # Detener propagación del evento
        
        # Hover effect (más intenso que el fondo base)
        def on_enter(e):
            hover_color = "#bbf7d0"  # green-200 - verde más intenso para hover
            card.configure(bg=hover_color)
            content_frame.configure(bg=hover_color)
            top_spacer.configure(bg=hover_color)
            content_container.configure(bg=hover_color)
            bottom_spacer.configure(bg=hover_color)
            icon_label.configure(bg=hover_color)
            title_label.configure(bg=hover_color)
        
        def on_leave(e):
            card.configure(bg=light_green_bg)
            content_frame.configure(bg=light_green_bg)
            top_spacer.configure(bg=light_green_bg)
            content_container.configure(bg=light_green_bg)
            bottom_spacer.configure(bg=light_green_bg)
            icon_label.configure(bg=light_green_bg)
            title_label.configure(bg=light_green_bg)
        
        # Hacer TODO el card clickeable - bind a todos los elementos
        # Esto asegura que cualquier parte del card responda al clic
        all_widgets = [card, content_frame, top_spacer, content_container, bottom_spacer, icon_label, title_label]
        for widget in all_widgets:
            widget.bind("<Button-1>", on_card_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        
        return card
    
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
        # Sección central: formulario de pago (padding mínimo)
        self.form_frame = tk.Frame(self, bg=self._content_bg)
        self.form_frame.pack(fill="x", padx=2, pady=(0, 2))
        self._build_register_payment_form()
        # Sección inferior: listado de pagos con scroll profesional
        self._create_payments_list_with_scroll()
        # Si hay un inquilino preseleccionado, autocompletar el campo y filtrar la tabla por ese inquilino
        if self.selected_tenant:
            self.tenant_autocomplete._select_tenant(self.selected_tenant)
            pagos = [p for p in self._get_all_payments() if p.get('id_inquilino') == self.selected_tenant.get('id')]
            self._display_register_payments(pagos)
        else:
            self._display_register_payments(self._get_all_payments())
        # Posicionar cursor en el cuadro de búsqueda al abrir la vista
        self.after(150, self._focus_search_entry_register)

    def _focus_search_entry_register(self):
        """Coloca el foco en el cuadro de búsqueda de inquilino (vista Registrar nuevo pago)."""
        if hasattr(self, "tenant_autocomplete") and hasattr(self.tenant_autocomplete, "entry"):
            if self.tenant_autocomplete.entry.winfo_exists():
                self.tenant_autocomplete.entry.focus_set()

    def _restore_global_title(self):
        try:
            self.master.master.page_title.configure(text="Control de Pagos")
        except Exception:
            pass
        self._create_layout()

    def _build_register_payment_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        row_opts = {'padx': (0, 8), 'pady': 2}
        # Fecha
        row1 = tk.Frame(self.form_frame, bg=cb)
        row1.pack(fill="x", pady=1)
        tk.Label(row1, text="Fecha de pago (DD/MM/YYYY):", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        tk.Entry(row1, textvariable=self.fecha_var, width=18).pack(side="left", **row_opts)
        # Monto
        row2 = tk.Frame(self.form_frame, bg=cb)
        row2.pack(fill="x", pady=1)
        tk.Label(row2, text="Monto:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        tk.Entry(row2, textvariable=self.monto_var, width=18).pack(side="left", **row_opts)
        # Método
        row3 = tk.Frame(self.form_frame, bg=cb)
        row3.pack(fill="x", pady=1)
        tk.Label(row3, text="Método:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        metodo_combo = ttk.Combobox(row3, textvariable=self.metodo_var, values=["Efectivo", "Transferencia", "Cheque"], width=16)
        metodo_combo.pack(side="left", **row_opts)
        # Observaciones
        row4 = tk.Frame(self.form_frame, bg=cb)
        row4.pack(fill="x", pady=1)
        tk.Label(row4, text="Observaciones:", width=22, anchor="w", bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        tk.Entry(row4, textvariable=self.obs_var, width=40).pack(side="left", **row_opts)
        # Botón guardar alineado a la IZQUIERDA - Verde para mantener tonalidad verde del módulo
        btn_save = tk.Button(
            self.form_frame,
            text="Registrar Pago",
            command=self._save_register_payment,
            bg="#22c55e",  # green-500 - verde para mantener tonalidad verde del módulo
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        btn_save.pack(pady=(4, 0), anchor="w")
        
        # Hover effect para botón registrar
        def on_enter_save(e):
            btn_save.configure(bg="#16a34a")  # green-600 - verde más oscuro para hover
        def on_leave_save(e):
            btn_save.configure(bg="#22c55e")  # green-500 - verde original
        btn_save.bind("<Enter>", on_enter_save)
        btn_save.bind("<Leave>", on_leave_save)

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
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        bg_alt = theme.get("bg_tertiary", "#f0f4fa")
        columns = getattr(self, '_table_columns', [
            ("Inquilino", 22), ("Fecha de pago", 14), ("Monto", 14), ("Método", 12), ("Observaciones", 38)
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
        from manager.app.paths_config import DOCUMENTOS_INQUILINOS_DIR, ensure_dirs, get_tenant_document_folder_name
        ensure_dirs()
        tenant = self.selected_tenant or {}
        folder_name = get_tenant_document_folder_name(tenant)
        tenant_dir = DOCUMENTOS_INQUILINOS_DIR / folder_name
        tenant_dir.mkdir(parents=True, exist_ok=True)
        fecha = pago.get("fecha_pago", "").replace("/", "-")
        filepath = str(tenant_dir / f"recibo_{fecha}.pdf")
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
        # Obtener el número real del apartamento (no el ID)
        apt_display = "N/A"
        if self.selected_tenant:
            apt_id = self.selected_tenant.get('apartamento', '')
            if apt_id:
                try:
                    apt = apartment_service.get_apartment_by_id(int(apt_id))
                    if apt and 'number' in apt:
                        apt_display = apt['number']
                    else:
                        apt_display = str(apt_id)
                except Exception:
                    apt_display = str(apt_id)
        c.drawString(50, y, f"Apartamento: {apt_display}")
        y -= 15
        c.drawString(50, y, f"Documento: {self.selected_tenant.get('numero_documento', '') if self.selected_tenant else 'N/A'}")
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
                        print(f"Error al navegar: {e}")
                        break
                widget = getattr(widget, 'master', None)
                depth += 1
            # Fallback: usar on_back si está disponible
            if self.on_back:
                self.on_back()
        
        edit_delete_view = EditDeletePaymentsView(
            self, 
            on_back=self._create_layout,
            on_payment_saved=self.on_payment_saved,
            on_navigate_to_dashboard=go_to_dashboard
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
                        print(f"Error al navegar: {e}")
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
            on_back=self._create_layout,
            on_navigate_to_dashboard=go_to_dashboard
        )
        reports_view.pack(fill="both", expand=True)

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
        # Botón guardar - Verde para mantener tonalidad verde del módulo
        btn_save = tk.Button(
            frame, 
            text="Guardar", 
            command=self._save,
            bg="#22c55e",  # green-500 - verde para mantener tonalidad verde del módulo
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2"
        )
        btn_save.pack(pady=(20, 0))
        
        # Hover effect para botón guardar
        def on_enter_save(e):
            btn_save.configure(bg="#16a34a")  # green-600 - verde más oscuro para hover
        def on_leave_save(e):
            btn_save.configure(bg="#22c55e")  # green-500 - verde original
        btn_save.bind("<Enter>", on_enter_save)
        btn_save.bind("<Leave>", on_leave_save)

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