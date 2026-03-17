"""
Vista de configuración del sistema
Permite configurar las credenciales SMTP para envío de emails
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from typing import Callable
import os
import webbrowser
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors
from manager.app.services.email_service import email_service
from manager.app.services.app_config_service import app_config_service
from manager.app.services.backup_service import backup_service


class SettingsView(tk.Frame):
    """Vista de configuración del sistema"""

    def __init__(self, parent, on_back: Callable = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.current_config = email_service.get_config()
        self.backup_config = app_config_service.get_backup_config()
        self.provider_var = tk.StringVar(value=self.current_config.get("provider", "gmail"))
        self.email_var = tk.StringVar(value=self.current_config.get("email", "") if self.current_config.get("email") else "")
        self.password_var = tk.StringVar(value="")
        self.sender_name_var = tk.StringVar(value=self.current_config.get("sender_name", "Building Manager Pro"))
        self.smtp_server_var = tk.StringVar(value=self.current_config.get("smtp_server", "smtp.gmail.com"))
        self.smtp_port_var = tk.StringVar(value=str(self.current_config.get("smtp_port", 587)))
        self.auto_backup_var = tk.BooleanVar(value=self.backup_config.get("auto_backup_enabled", True))
        self.backup_interval_var = tk.IntVar(value=self.backup_config.get("interval_hours", 6))
        self.max_backups_var = tk.IntVar(value=self.backup_config.get("max_backups", 10))
        self.auto_backup_password_var = tk.StringVar(value=self.backup_config.get("auto_backup_password", "") or "")
        self.cloud_folder_var = tk.StringVar(value=self.backup_config.get("cloud_folder", "") or "")

        # Modo desarrollador (para herramientas de prueba)
        self._dev_mode = os.environ.get("BM_DEV_MODE", "").strip() == "1"
        lic = app_config_service.get_license_config()
        self.license_test_mode_var = tk.BooleanVar(value=bool(lic.get("test_mode")))
        self.license_demo_days_var = tk.IntVar(value=int(lic.get("demo_days_override") or 1))
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal"""
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        fg = theme.get("text_primary", "#1f2937")
        header_frame = tk.Frame(self, bg=cb)
        header_frame.pack(fill="x", padx=Spacing.MD, pady=(0, 2))
        title_label = tk.Label(header_frame, text="⚙️ Configuración del Sistema", font=("Segoe UI", 16, "bold"), bg=cb, fg=fg)
        title_label.pack(side="left")
        buttons_frame = tk.Frame(header_frame, bg=cb)
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame, self.on_back)
        sep_color = theme.get("border_light", "#e5e7eb")
        sep = tk.Frame(self, height=1, bg=sep_color)
        sep.pack(fill="x", padx=Spacing.MD, pady=(0, 2))
        scroll_container = tk.Frame(self, bg=cb)
        scroll_container.pack(fill="both", expand=True)
        canvas = tk.Canvas(scroll_container, bg=cb, highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=cb)
        
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
        
        canvas.pack(side="left", fill="both", expand=True, padx=Spacing.MD, pady=(0, 2))
        scrollbar.pack(side="right", fill="y")
        self._create_backup_config_section(content_frame)
        self._create_section_separator(content_frame)
        self._create_email_config_section(content_frame)
        self._create_section_separator(content_frame)
        self._create_license_section(content_frame)
        if self._dev_mode:
            self._create_section_separator(content_frame)
            self._create_license_test_section(content_frame)
    
    def _create_section_separator(self, parent):
        """Dibuja una línea separadora entre secciones de configuración (sin bordes de tarjeta)."""
        cb = self._content_bg
        sep_color = theme_manager.themes[theme_manager.current_theme].get("border_light", "#e5e7eb")
        container = tk.Frame(parent, bg=cb)
        container.pack(fill="x", pady=(Spacing.SM, Spacing.SM))
        line = tk.Frame(container, height=1, bg=sep_color)
        line.pack(fill="x")
        line.pack_propagate(False)

    def _create_backup_config_section(self, parent):
        """Crea la sección de configuración de backups"""
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        fg_sec = "#374151"
        backup_card = tk.Frame(parent, bg=cb)
        backup_card.pack(fill="x", pady=(0, 0))
        card_content = tk.Frame(backup_card, bg=cb)
        card_content.pack(fill="both", expand=True, padx=Spacing.MD, pady=3)
        section_title = tk.Label(card_content, text="💾 Backups Automáticos", font=("Segoe UI", 12, "bold"), bg=cb, fg=fg)
        section_title.pack(anchor="w", pady=(0, 2))
        auto_backup_frame = tk.Frame(card_content, bg=cb)
        auto_backup_frame.pack(fill="x", pady=(0, 2))
        auto_backup_check = tk.Checkbutton(
            auto_backup_frame, text="Habilitar backups automáticos", variable=self.auto_backup_var,
            font=("Segoe UI", 10), fg=fg, bg=cb, activebackground=cb, activeforeground=fg, selectcolor=cb,
            command=self._on_auto_backup_toggle
        )
        auto_backup_check.pack(anchor="w")
        interval_frame = tk.Frame(card_content, bg=cb)
        interval_frame.pack(fill="x", pady=(0, 4))
        tk.Label(interval_frame, text="Intervalo (horas):", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 2))
        interval_spinbox = tk.Spinbox(interval_frame, from_=1, to=24, textvariable=self.backup_interval_var, font=("Segoe UI", 10), width=8)
        interval_spinbox.pack(anchor="w")
        max_backups_frame = tk.Frame(card_content, bg=cb)
        max_backups_frame.pack(fill="x", pady=(0, 4))
        tk.Label(card_content, text="Contraseña para backups automáticos (opcional):", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(4, 2))
        auto_pwd_entry = tk.Entry(card_content, textvariable=self.auto_backup_password_var, font=("Segoe UI", 10), width=35, show="*")
        auto_pwd_entry.pack(fill="x", pady=(0, 2))
        tk.Label(card_content, text="Si la define, los backups automáticos se cifrarán con AES.", font=("Segoe UI", 8), fg=fg_sec, bg=cb).pack(anchor="w")
        tk.Label(card_content, text="Carpeta en la nube (Google Drive / OneDrive):", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(4, 2))
        cloud_row = tk.Frame(card_content, bg=cb)
        cloud_row.pack(fill="x", pady=(0, 2))
        cloud_entry = tk.Entry(cloud_row, textvariable=self.cloud_folder_var, font=("Segoe UI", 10), width=32)
        cloud_entry.pack(side="left", fill="x", expand=True)
        tk.Button(cloud_row, text="Examinar…", font=("Segoe UI", 9), command=self._browse_cloud_folder).pack(side="right", padx=(8, 0))
        tk.Label(card_content, text="Ruta de la carpeta local que se sincroniza con la nube.", font=("Segoe UI", 8), fg=fg_sec, bg=cb).pack(anchor="w")
        status_frame = tk.Frame(card_content, bg=cb)
        status_frame.pack(fill="x", pady=(4, 0))
        backup_status = backup_service.get_backup_status()
        status_text = f"Estado: {'✅ Activo' if backup_status['enabled'] else '⏸️ Inactivo'} | Total: {backup_status['total_backups']}"
        if backup_status['enabled']:
            status_text += f" | Próximo: {backup_status.get('next_backup', 'N/A')}"
        tk.Label(status_frame, text=status_text, font=("Segoe UI", 9), fg=fg_sec, bg=cb).pack(anchor="w")
        btn_row = tk.Frame(card_content, bg=cb)
        btn_row.pack(fill="x", pady=(4, 0))
        save_btn = ModernButton(btn_row, text="Guardar configuración", icon=Icons.SAVE, style="purple", small=True, command=self._save_backup_config)
        save_btn.pack(side="left", padx=(0, Spacing.SM))
        create_now_btn = ModernButton(btn_row, text="Crear backup ahora", icon="💾", style="secondary", small=True, command=self._create_backup_now)
        create_now_btn.pack(side="left")
    
    def _on_auto_backup_toggle(self):
        """Maneja el toggle de backups automáticos"""
        pass

    def _browse_cloud_folder(self):
        """Abre el diálogo para elegir la carpeta en la nube (Google Drive / OneDrive)."""
        path = filedialog.askdirectory(title="Seleccionar carpeta en la nube (Google Drive / OneDrive)")
        if path:
            self.cloud_folder_var.set(path)

    def _create_backup_now(self):
        """Crea un backup y lo guarda en la carpeta en la nube configurada. Exige que la ruta esté establecida."""
        cloud_path = (self.cloud_folder_var.get() or "").strip()
        if not cloud_path:
            messagebox.showerror(
                "Ruta de respaldo requerida",
                "Debe establecer primero una ruta de respaldo en la nube.\n\n"
                "Use el campo \"Carpeta en la nube (Google Drive / OneDrive)\" y el botón \"Examinar...\" "
                "para seleccionar la carpeta, luego guarde la configuración si desea conservarla."
            )
            return
        path = backup_service.create_full_backup(output_path=cloud_path, is_auto=True)
        if path:
            messagebox.showinfo("Backup creado", f"Backup guardado correctamente en:\n{path}")
        else:
            messagebox.showerror("Error", "No se pudo crear el backup.")

    def _save_backup_config(self):
        """Guarda la configuración de backups con trazabilidad"""
        from manager.app.services.user_service import user_service

        backup_config = {
            "auto_backup_enabled": self.auto_backup_var.get(),
            "interval_hours": self.backup_interval_var.get(),
            "max_backups": 5,
            "auto_backup_password": (self.auto_backup_password_var.get() or "").strip(),
            "cloud_folder": (self.cloud_folder_var.get() or "").strip(),
        }

        if app_config_service.set_backup_config(backup_config):
            backup_service.set_max_backups(backup_config["max_backups"])
            if backup_config["auto_backup_enabled"]:
                backup_service.start_auto_backup(backup_config["interval_hours"])
            else:
                backup_service.stop_auto_backup()
            try:
                username = "admin"
                status = "activado" if backup_config["auto_backup_enabled"] else "desactivado"
                user_service._log_activity(
                    username,
                    "config_changed",
                    f"Backups automáticos {status} | Intervalo: {backup_config['interval_hours']}h | Máximo: {backup_config['max_backups']}",
                    None,
                )
            except Exception as e:
                pass
            messagebox.showinfo("✅ Configuración guardada", "La configuración de backups se ha guardado correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración de backups.")
    
    def _create_email_config_section(self, parent):
        """Crea la sección de configuración de email"""
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        fg_sec = "#374151"
        email_card = tk.Frame(parent, bg=cb)
        email_card.pack(fill="x", pady=(0, 0))
        card_content = tk.Frame(email_card, bg=cb)
        card_content.pack(fill="both", expand=True, padx=Spacing.MD, pady=3)
        section_title = tk.Label(card_content, text="📧 Email SMTP", font=("Segoe UI", 12, "bold"), bg=cb, fg=fg)
        section_title.pack(anchor="w", pady=(0, 2))
        description = tk.Label(card_content, text="Credenciales SMTP para enviar recibos por email.", font=("Segoe UI", 9), fg=fg_sec, bg=cb)
        description.pack(anchor="w", pady=(0, 2))
        provider_frame = tk.Frame(card_content, bg=cb)
        provider_frame.pack(fill="x", pady=(0, 2))
        tk.Label(provider_frame, text="Proveedor:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 1))
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.provider_var, values=["gmail", "outlook", "custom"], state="readonly", width=18, font=("Segoe UI", 10))
        provider_combo.pack(anchor="w")
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_changed)
        email_frame = tk.Frame(card_content, bg=cb)
        email_frame.pack(fill="x", pady=(0, 2))
        tk.Label(email_frame, text="Email:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 1))
        email_entry = tk.Entry(email_frame, textvariable=self.email_var, font=("Segoe UI", 10), width=40)
        email_entry.pack(fill="x")
        password_frame = tk.Frame(card_content, bg=cb)
        password_frame.pack(fill="x", pady=(0, 2))
        password_label_row = tk.Frame(password_frame, bg=cb)
        password_label_row.pack(fill="x", pady=(0, 1))
        tk.Label(password_label_row, text="Contraseña de aplicación:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(side="left")
        help_btn = tk.Button(
            password_label_row,
            text=" ¿Ayuda? ",
            font=("Segoe UI", 9),
            fg="#2563eb",
            bg=cb,
            activeforeground="#1d4ed8",
            activebackground=cb,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._show_app_password_help,
        )
        help_btn.pack(side="left", padx=(8, 0))
        help_btn.bind("<Enter>", lambda e: help_btn.configure(fg="#1d4ed8"))
        help_btn.bind("<Leave>", lambda e: help_btn.configure(fg="#2563eb"))
        password_entry = tk.Entry(password_frame, textvariable=self.password_var, font=("Segoe UI", 10), width=40, show="*")
        password_entry.pack(fill="x")
        help_label = tk.Label(password_frame, text="💡 Use contraseña de aplicación (Gmail/Outlook).", font=("Segoe UI", 8), fg=fg_sec, bg=cb, wraplength=500)
        help_label.pack(anchor="w", pady=(1, 0))
        sender_name_frame = tk.Frame(card_content, bg=cb)
        sender_name_frame.pack(fill="x", pady=(0, 2))
        tk.Label(sender_name_frame, text="Nombre remitente:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 1))
        sender_name_entry = tk.Entry(sender_name_frame, textvariable=self.sender_name_var, font=("Segoe UI", 10), width=40)
        sender_name_entry.pack(fill="x")
        self.custom_fields_frame = tk.Frame(card_content, bg=cb)
        self._update_custom_fields_visibility()
        status_frame = tk.Frame(card_content, bg=cb)
        status_frame.pack(fill="x", pady=(2, 0))
        is_configured = email_service.is_configured()
        status_text = "✅ Configuración completa" if is_configured else "⚠️ Configuración incompleta"
        status_color = "#16a34a" if is_configured else "#d97706"
        tk.Label(status_frame, text=status_text, font=("Segoe UI", 9, "bold"), fg=status_color, bg=cb).pack(anchor="w")
        buttons_frame = tk.Frame(card_content, bg=cb)
        buttons_frame.pack(fill="x", pady=(4, 0))
        save_btn = ModernButton(buttons_frame, text="Guardar", icon=Icons.SAVE, style="purple", small=True, command=self._save_email_config)
        save_btn.pack(side="left", padx=(0, Spacing.SM))
        test_btn = ModernButton(buttons_frame, text="Probar", icon="🔍", style="secondary", small=True, command=self._test_email_connection)
        test_btn.pack(side="left")

    def _show_app_password_help(self):
        """Muestra ventana de ayuda con instrucciones oficiales para contraseñas de aplicación (Gmail y Outlook)."""
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = theme.get("bg_primary", "#ffffff")
        fg = theme.get("text_primary", "#1f2937")
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Ayuda: Contraseña de aplicación")
        win.configure(bg=cb)
        win.geometry("520x480")
        win.minsize(400, 360)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        # Contenido con scroll
        text_frame = tk.Frame(win, bg=cb)
        text_frame.pack(fill="both", expand=True, padx=12, pady=(8, 4))
        scroll = tk.Scrollbar(text_frame)
        text = tk.Text(
            text_frame,
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            bg=cb,
            fg=fg,
            relief="flat",
            padx=8,
            pady=8,
            yscrollcommand=scroll.set,
        )
        scroll.config(command=text.yview)
        scroll.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)
        content = """Contraseñas de aplicación permiten que programas como Building Manager Pro envíen correos usando tu cuenta sin usar tu contraseña normal. Son necesarias cuando tienes verificación en dos pasos activada.

━━━ GMAIL (Google) ━━━

1. Entra en tu Cuenta de Google: https://myaccount.google.com/
2. Ve a Seguridad → Verificación en dos pasos (debe estar activada).
3. Al final de la página, en "Contraseñas de aplicaciones", elige "Contraseñas de aplicaciones".
4. Selecciona "Correo" y "Otro (nombre personalizado)", escribe por ejemplo "Building Manager Pro".
5. Haz clic en "Generar". Google mostrará una contraseña de 16 caracteres; cópiala y pégala aquí (sin espacios).

Enlace oficial: https://support.google.com/accounts/answer/185833

━━━ OUTLOOK / MICROSOFT 365 ━━━

1. Entra en tu cuenta Microsoft: https://account.microsoft.com/security
2. Ve a "Opciones de seguridad avanzadas" o "Contraseñas de aplicaciones".
3. En "Contraseñas de aplicaciones", crea una nueva. Puede pedirte que confirmes con tu contraseña o verificación en dos pasos.
4. Asigna un nombre (ej. "Building Manager Pro") y genera la contraseña.
5. Copia la contraseña de 16 caracteres y pégala aquí.

Enlace oficial: https://support.microsoft.com/es-es/account-billing/crear-contraseñas-de-aplicacion-para-la-verificacion-en-dos-pasos-5896ed9b-4263-e681-128a-a6f2979a7944

━━━ NOTA ━━━

• No uses tu contraseña normal de correo; no funcionará si tienes 2FA activada.
• La contraseña de aplicación solo se muestra una vez al crearla; guárdala en un lugar seguro.
"""
        text.insert("1.0", content.strip())
        text.config(state="disabled")
        # Botones: enlaces y cerrar
        btn_frame = tk.Frame(win, bg=cb)
        btn_frame.pack(fill="x", padx=12, pady=(4, 10))
        tk.Button(
            btn_frame,
            text=" Abrir ayuda Gmail (oficial) ",
            font=("Segoe UI", 9),
            fg="#1a73e8",
            bg=cb,
            relief="flat",
            cursor="hand2",
            command=lambda: webbrowser.open("https://support.google.com/accounts/answer/185833"),
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_frame,
            text=" Abrir ayuda Outlook (oficial) ",
            font=("Segoe UI", 9),
            fg="#0078d4",
            bg=cb,
            relief="flat",
            cursor="hand2",
            command=lambda: webbrowser.open("https://support.microsoft.com/es-es/account-billing/crear-contraseñas-de-aplicacion-para-la-verificacion-en-dos-pasos-5896ed9b-4263-e681-128a-a6f2979a7944"),
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_frame,
            text=" Cerrar ",
            font=("Segoe UI", 10),
            bg=theme.get("bg_tertiary", "#e5e7eb"),
            fg=fg,
            relief="flat",
            cursor="hand2",
            command=win.destroy,
        ).pack(side="right")
        win.protocol("WM_DELETE_WINDOW", win.destroy)
        win.focus_set()

    def _create_license_test_section(self, parent):
        """Sección de modo prueba de licencias (solo desarrollo: BM_DEV_MODE=1)."""
        from manager.app.services.license_service import license_service

        cb = self._content_bg
        theme = theme_manager.themes[theme_manager.current_theme]
        fg = theme.get("text_primary", "#1f2937")
        fg_sec = theme.get("text_secondary", "#374151")

        card = tk.Frame(parent, bg=cb)
        card.pack(fill="x", pady=(0, 0))
        content = tk.Frame(card, bg=cb)
        content.pack(fill="both", expand=True, padx=Spacing.MD, pady=3)

        tk.Label(content, text="🔑 Licencias (modo prueba)", font=("Segoe UI", 12, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 2))
        tk.Label(
            content,
            text="Solo para desarrollo. Activa BM_DEV_MODE=1 para habilitar estas opciones.",
            font=("Segoe UI", 9),
            bg=cb,
            fg=fg_sec,
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(0, 4))

        row = tk.Frame(content, bg=cb)
        row.pack(fill="x", pady=(0, 2))
        tk.Checkbutton(
            row,
            text="Habilitar modo prueba",
            variable=self.license_test_mode_var,
            font=("Segoe UI", 10),
            fg=fg,
            bg=cb,
            activebackground=cb,
            activeforeground=fg,
            selectcolor=cb,
        ).pack(side="left")

        days_frame = tk.Frame(content, bg=cb)
        days_frame.pack(fill="x", pady=(0, 4))
        tk.Label(days_frame, text="Días de demo (prueba):", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(side="left")
        tk.Spinbox(days_frame, from_=0, to=60, textvariable=self.license_demo_days_var, font=("Segoe UI", 10), width=6).pack(side="left", padx=(Spacing.SM, 0))

        status_var = tk.StringVar(value="")
        status_lbl = tk.Label(content, textvariable=status_var, font=("Segoe UI", 9), bg=cb, fg=fg_sec)
        status_lbl.pack(anchor="w", pady=(0, 4))

        def refresh_status():
            st = license_service.get_status()
            mode = st.get("mode")
            rem = st.get("remaining_days")
            status_var.set(f"Estado actual: {mode} | Días restantes: {rem}")

        def apply_test():
            if self.license_test_mode_var.get():
                ok = license_service.enable_test_mode(self.license_demo_days_var.get())
                if not ok:
                    messagebox.showwarning("Licencias", "Modo prueba disponible solo con BM_DEV_MODE=1.", parent=self.winfo_toplevel())
            else:
                license_service.disable_test_mode()
            refresh_status()

        def force_expired():
            ok = license_service.force_expired_demo()
            if not ok:
                messagebox.showwarning("Licencias", "Modo prueba disponible solo con BM_DEV_MODE=1.", parent=self.winfo_toplevel())
            refresh_status()

        def restore_demo():
            ok = license_service.reset_demo(30)
            if not ok:
                messagebox.showwarning("Licencias", "Modo prueba disponible solo con BM_DEV_MODE=1.", parent=self.winfo_toplevel())
            refresh_status()

        btns = tk.Frame(content, bg=cb)
        btns.pack(fill="x", pady=(2, 0))
        ModernButton(btns, text="Aplicar", icon=Icons.SAVE, style="purple", small=True, command=apply_test).pack(side="left", padx=(0, Spacing.SM))
        ModernButton(btns, text="Forzar vencimiento", icon="⛔", style="secondary", small=True, command=force_expired).pack(side="left", padx=(0, Spacing.SM))
        ModernButton(btns, text="Restaurar demo 30 días", icon="↩", style="secondary", small=True, command=restore_demo).pack(side="left")

        refresh_status()

    def _create_license_section(self, parent):
        """Sección de licencia (usuarios finales): estado actual y activación."""
        from manager.app.services.license_service import license_service

        cb = self._content_bg
        theme = theme_manager.themes[theme_manager.current_theme]
        fg = theme.get("text_primary", "#1f2937")
        fg_sec = theme.get("text_secondary", "#374151")

        card = tk.Frame(parent, bg=cb)
        card.pack(fill="x", pady=(0, 0))
        content = tk.Frame(card, bg=cb)
        content.pack(fill="both", expand=True, padx=Spacing.MD, pady=3)

        tk.Label(content, text="🔑 Licencia", font=("Segoe UI", 12, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 2))

        status_var = tk.StringVar(value="")
        status_lbl = tk.Label(content, textvariable=status_var, font=("Segoe UI", 10), bg=cb, fg=fg_sec, justify="left", wraplength=900)
        status_lbl.pack(anchor="w", pady=(0, 6))

        def refresh_status():
            st = license_service.get_status()
            mode = st.get("mode")
            rem = st.get("remaining_days")
            if mode == "licensed":
                exp = st.get("license_expires_at")
                exp_txt = exp.strftime("%d/%m/%Y") if exp else "N/A"
                status_var.set(f"Estado: Licencia activa. Vence el {exp_txt}.")
            elif mode == "demo":
                status_var.set(f"Estado: Demostración activa. Te quedan {rem} días.")
            else:
                status_var.set("Estado: Demostración vencida o licencia expirada. Activa tu licencia para continuar.")

        def open_activate_dialog():
            # Diálogo modal para ingresar clave y validar con Keygen
            win = tk.Toplevel(self.winfo_toplevel())
            win.title("Activar licencia")
            win.geometry("520x260")
            win.transient(self.winfo_toplevel())
            win.grab_set()
            win.resizable(False, False)

            bg = theme.get("bg_primary", "#ffffff")
            win.configure(bg=bg)
            inner = tk.Frame(win, bg=bg, padx=Spacing.LG, pady=Spacing.LG)
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text="Activar licencia", font=("Segoe UI", 14, "bold"), bg=bg, fg=fg).pack(anchor="w", pady=(0, Spacing.SM))
            tk.Label(
                inner,
                text="Ingrese su clave de licencia anual para activar el software.",
                font=("Segoe UI", 10),
                bg=bg,
                fg=theme.get("text_secondary", "#6b7280"),
                justify="left",
                wraplength=480,
            ).pack(anchor="w", pady=(0, Spacing.MD))

            tk.Label(inner, text="Clave de licencia:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w")
            key_var = tk.StringVar()
            entry = tk.Entry(inner, textvariable=key_var, font=("Segoe UI", 10))
            entry.pack(fill="x", pady=(2, 0))
            entry.focus_set()

            msg_var = tk.StringVar(value="")
            tk.Label(inner, textvariable=msg_var, font=("Segoe UI", 9), bg=bg, fg="#b91c1c", justify="left", wraplength=480).pack(anchor="w", pady=(4, 0))

            btns = tk.Frame(inner, bg=bg)
            btns.pack(fill="x", pady=(Spacing.LG, 0))

            def do_activate():
                key = key_var.get().strip()
                result = license_service.validate_key_with_keygen(key)
                if not result.get("ok"):
                    msg_var.set(result.get("message", "No se pudo validar la licencia."))
                    return
                license_service.activate_license(key, result.get("expires_at"))
                msg_var.set("")
                messagebox.showinfo("Licencia activada", "La licencia se ha activado correctamente.", parent=win)
                win.destroy()
                refresh_status()

            ModernButton(btns, text="Activar", icon="✅", style="primary", small=True, command=do_activate).pack(side="right")
            ModernButton(btns, text="Cancelar", icon="✖", style="secondary", small=True, command=win.destroy).pack(side="right", padx=(0, Spacing.SM))

            win.protocol("WM_DELETE_WINDOW", win.destroy)

        actions = tk.Frame(content, bg=cb)
        actions.pack(fill="x")
        ModernButton(actions, text="Activar licencia", icon="🔐", style="primary", small=True, command=open_activate_dialog).pack(side="left")
        ModernButton(actions, text="Actualizar estado", icon="🔄", style="secondary", small=True, command=refresh_status).pack(side="left", padx=(Spacing.SM, 0))

        refresh_status()
    
    def _create_custom_fields(self):
        """Crea los campos personalizados para proveedor custom"""
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        for widget in self.custom_fields_frame.winfo_children():
            widget.destroy()
        smtp_server_frame = tk.Frame(self.custom_fields_frame, bg=cb)
        smtp_server_frame.pack(fill="x", pady=(0, 4))
        tk.Label(smtp_server_frame, text="Servidor SMTP:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 2))
        tk.Entry(smtp_server_frame, textvariable=self.smtp_server_var, font=("Segoe UI", 10), width=40).pack(fill="x")
        smtp_port_frame = tk.Frame(self.custom_fields_frame, bg=cb)
        smtp_port_frame.pack(fill="x", pady=(0, 4))
        tk.Label(smtp_port_frame, text="Puerto SMTP:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(anchor="w", pady=(0, 2))
        tk.Entry(smtp_port_frame, textvariable=self.smtp_port_var, font=("Segoe UI", 10), width=8).pack(anchor="w")
    
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
                self.custom_fields_frame.pack(fill="x", pady=(0, 4))
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
            # Registrar actividad
            try:
                from manager.app.services.user_service import user_service
                username = "admin"
                provider = config_data.get("provider", "custom")
                user_service._log_activity(
                    username,
                    "config_changed",
                    f"Configuración de email SMTP actualizada: {provider} ({email})",
                    None
                )
            except Exception as e:
                print(f"Error al registrar actividad: {e}")
            
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
    
    def _create_navigation_buttons(self, parent, on_back_command):
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]

        def go_to_dashboard():
            if self.on_back:
                self.on_back()

        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=14,
            pady=6,
            radius=4,
            border_color=purple_hover
        )
        btn_dashboard.pack(side="right")
