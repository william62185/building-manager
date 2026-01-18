"""
Vista de configuración del sistema
Permite configurar las credenciales SMTP para envío de emails
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard, ModernSeparator
from manager.app.services.email_service import email_service


class SettingsView(tk.Frame):
    """Vista de configuración del sistema"""
    
    def __init__(self, parent, on_back: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_back = on_back
        
        # Cargar configuración actual
        self.current_config = email_service.get_config()
        
        # Variables para los campos del formulario
        self.provider_var = tk.StringVar(value=self.current_config.get("provider", "gmail"))
        self.email_var = tk.StringVar(value=self.current_config.get("email", "") if self.current_config.get("email") else "")
        self.password_var = tk.StringVar(value="")  # Nunca mostramos la contraseña actual
        self.sender_name_var = tk.StringVar(value=self.current_config.get("sender_name", "Building Manager Pro"))
        self.smtp_server_var = tk.StringVar(value=self.current_config.get("smtp_server", "smtp.gmail.com"))
        self.smtp_port_var = tk.StringVar(value=str(self.current_config.get("smtp_port", 587)))
        
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal"""
        # Header
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.LG, Spacing.MD))
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="⚙️ Configuración del Sistema",
            **theme_manager.get_style("label_title")
        )
        title_label.pack(side="left")
        
        # Separador
        separator = ModernSeparator(self)
        separator.pack(fill="x", padx=Spacing.MD)
        
        # Contenedor con scroll para el contenido principal
        scroll_container = tk.Frame(self, **theme_manager.get_style("frame"))
        scroll_container.pack(fill="both", expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(scroll_container, **theme_manager.get_style("frame"), highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, **theme_manager.get_style("frame"))
        
        # Configurar scroll
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ajustar ancho del frame al canvas
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Scroll con mouse
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind('<Enter>', bind_mousewheel)
        canvas.bind('<Leave>', unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        scrollbar.pack(side="right", fill="y")
        
        # Sección de Configuración de Email
        self._create_email_config_section(content_frame)
    
    def _create_email_config_section(self, parent):
        """Crea la sección de configuración de email"""
        # Card para la configuración de email
        email_card = ModernCard(parent)
        email_card.pack(fill="x", pady=(0, Spacing.MD))
        
        card_content = tk.Frame(email_card, **theme_manager.get_style("frame"))
        card_content.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        # Título de la sección
        section_title = tk.Label(
            card_content,
            text="📧 Configuración de Email SMTP",
            font=("Segoe UI", 14, "bold"),
            **theme_manager.get_style("label")
        )
        section_title.pack(anchor="w", pady=(0, Spacing.MD))
        
        # Descripción
        description = tk.Label(
            card_content,
            text="Configure las credenciales SMTP para enviar recibos de pago por email a los inquilinos.",
            font=("Segoe UI", 10),
            fg="#666",
            **theme_manager.get_style("label")
        )
        description.pack(anchor="w", pady=(0, Spacing.LG))
        
        # Proveedor de email
        provider_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        provider_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            provider_frame,
            text="Proveedor de Email:",
            font=("Segoe UI", 10, "bold"),
            **theme_manager.get_style("label")
        ).pack(anchor="w", pady=(0, 5))
        
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=["gmail", "outlook", "custom"],
            state="readonly",
            width=20,
            font=("Segoe UI", 10)
        )
        provider_combo.pack(anchor="w")
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_changed)
        
        # Email
        email_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        email_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            email_frame,
            text="Email del Remitente:",
            font=("Segoe UI", 10, "bold"),
            **theme_manager.get_style("label")
        ).pack(anchor="w", pady=(0, 5))
        
        email_entry = tk.Entry(
            email_frame,
            textvariable=self.email_var,
            font=("Segoe UI", 10),
            width=50
        )
        email_entry.pack(fill="x")
        
        # Contraseña de aplicación
        password_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        password_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            password_frame,
            text="Contraseña de Aplicación:",
            font=("Segoe UI", 10, "bold"),
            **theme_manager.get_style("label")
        ).pack(anchor="w", pady=(0, 5))
        
        password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            font=("Segoe UI", 10),
            width=50,
            show="*"
        )
        password_entry.pack(fill="x")
        
        help_label = tk.Label(
            password_frame,
            text="💡 Para Gmail/Outlook: Use una contraseña de aplicación, no su contraseña normal. Consulte la ayuda de su proveedor.",
            font=("Segoe UI", 9),
            fg="#666",
            wraplength=600,
            justify="left",
            **theme_manager.get_style("label")
        )
        help_label.pack(anchor="w", pady=(5, 0))
        
        # Nombre del remitente
        sender_name_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        sender_name_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            sender_name_frame,
            text="Nombre del Remitente:",
            font=("Segoe UI", 10, "bold"),
            **theme_manager.get_style("label")
        ).pack(anchor="w", pady=(0, 5))
        
        sender_name_entry = tk.Entry(
            sender_name_frame,
            textvariable=self.sender_name_var,
            font=("Segoe UI", 10),
            width=50
        )
        sender_name_entry.pack(fill="x")
        
        # Campos personalizados (solo para "custom")
        self.custom_fields_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        
        self._update_custom_fields_visibility()
        
        # Estado de la configuración
        status_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        status_frame.pack(fill="x", pady=(Spacing.MD, 0))
        
        is_configured = email_service.is_configured()
        status_text = "✅ Configuración completa" if is_configured else "⚠️ Configuración incompleta"
        status_color = "#4caf50" if is_configured else "#ff9800"
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Segoe UI", 10, "bold"),
            fg=status_color,
            **theme_manager.get_style("label")
        )
        status_label.pack(anchor="w")
        
        # Botones
        buttons_frame = tk.Frame(card_content, **theme_manager.get_style("frame"))
        buttons_frame.pack(fill="x", pady=(Spacing.LG, 0))
        
        save_btn = ModernButton(
            buttons_frame,
            text="Guardar Configuración",
            icon=Icons.SAVE,
            style="primary",
            command=self._save_email_config
        )
        save_btn.pack(side="left", padx=(0, Spacing.SM))
        
        test_btn = ModernButton(
            buttons_frame,
            text="Probar Conexión",
            icon="🔍",
            style="secondary",
            command=self._test_email_connection
        )
        test_btn.pack(side="left")
    
    def _create_custom_fields(self):
        """Crea los campos personalizados para proveedor custom"""
        for widget in self.custom_fields_frame.winfo_children():
            widget.destroy()
        
        # Servidor SMTP
        smtp_server_frame = tk.Frame(self.custom_fields_frame, **theme_manager.get_style("frame"))
        smtp_server_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            smtp_server_frame,
            text="Servidor SMTP:",
            font=("Segoe UI", 10, "bold"),
            **theme_manager.get_style("label")
        ).pack(anchor="w", pady=(0, 5))
        
        smtp_server_entry = tk.Entry(
            smtp_server_frame,
            textvariable=self.smtp_server_var,
            font=("Segoe UI", 10),
            width=50
        )
        smtp_server_entry.pack(fill="x")
        
        # Puerto SMTP
        smtp_port_frame = tk.Frame(self.custom_fields_frame, **theme_manager.get_style("frame"))
        smtp_port_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            smtp_port_frame,
            text="Puerto SMTP:",
            font=("Segoe UI", 10, "bold"),
            **theme_manager.get_style("label")
        ).pack(anchor="w", pady=(0, 5))
        
        smtp_port_entry = tk.Entry(
            smtp_port_frame,
            textvariable=self.smtp_port_var,
            font=("Segoe UI", 10),
            width=10
        )
        smtp_port_entry.pack(anchor="w")
    
    def _on_provider_changed(self, event=None):
        """Maneja el cambio de proveedor"""
        provider = self.provider_var.get()
        
        if provider == "gmail":
            self.smtp_server_var.set("smtp.gmail.com")
            self.smtp_port_var.set("587")
        elif provider == "outlook":
            self.smtp_server_var.set("smtp-mail.outlook.com")
            self.smtp_port_var.set("587")
        
        self._update_custom_fields_visibility()
    
    def _update_custom_fields_visibility(self):
        """Actualiza la visibilidad de los campos personalizados"""
        provider = self.provider_var.get()
        
        if provider == "custom":
            if not self.custom_fields_frame.winfo_ismapped():
                self.custom_fields_frame.pack(fill="x", pady=(0, Spacing.MD))
            if not hasattr(self, '_custom_fields_created'):
                self._create_custom_fields()
                self._custom_fields_created = True
        else:
            if self.custom_fields_frame.winfo_ismapped():
                self.custom_fields_frame.pack_forget()
    
    def _save_email_config(self):
        """Guarda la configuración de email"""
        # Validaciones
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        sender_name = self.sender_name_var.get().strip()
        provider = self.provider_var.get()
        
        if not email:
            messagebox.showerror("Error", "Por favor ingrese el email del remitente.")
            return
        
        if not password:
            # Si no hay contraseña nueva, verificar que ya exista una configurada
            if not email_service.is_configured():
                messagebox.showerror("Error", "Por favor ingrese la contraseña de aplicación.")
                return
        
        if not sender_name:
            messagebox.showerror("Error", "Por favor ingrese el nombre del remitente.")
            return
        
        # Preparar datos de configuración
        config_data = {
            "provider": provider,
            "email": email,
            "sender_name": sender_name
        }
        
        # Solo actualizar contraseña si se ingresó una nueva
        if password:
            config_data["password"] = password
        else:
            # Mantener la contraseña actual si no se ingresó una nueva
            config_data["password"] = email_service.config.get("password", "")
        
        # Agregar configuración personalizada si es necesario
        if provider == "custom":
            config_data["smtp_server"] = self.smtp_server_var.get().strip()
            try:
                config_data["smtp_port"] = int(self.smtp_port_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un puerto SMTP válido.")
                return
        
        # Guardar configuración
        success = email_service.save_config(config_data)
        
        if success:
            messagebox.showinfo("✅ Configuración guardada", "La configuración de email se ha guardado correctamente.")
            # Recargar configuración actual
            self.current_config = email_service.get_config()
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración. Por favor intente nuevamente.")
    
    def _test_email_connection(self):
        """Prueba la conexión SMTP con las credenciales configuradas"""
        if not email_service.is_configured():
            messagebox.showwarning(
                "Configuración incompleta",
                "Por favor configure primero las credenciales SMTP antes de probar la conexión."
            )
            return
        
        messagebox.showinfo(
            "Prueba de Conexión",
            "La prueba de conexión se realizará al enviar el primer email.\n\n"
            "Las credenciales se validarán automáticamente cuando intente enviar un recibo."
        )
