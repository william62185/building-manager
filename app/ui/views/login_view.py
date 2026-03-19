"""
Vista de inicio de sesión.
Se muestra al arrancar la app cuando ya existen usuarios.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Callable, Dict, Any

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import bind_combobox_dropdown_on_click
from manager.app.services.user_service import user_service
from manager.app.services.email_service import email_service
from manager.app.logger import logger


class LoginView(tk.Frame):
    """Pantalla de login: usuario y contraseña. Al validar llama on_success(user)."""

    def __init__(self, parent, on_success: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_success = on_success
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("bg_primary", "#ffffff")
        self._fg = theme.get("text_primary", "#1e293b")
        self.configure(bg=self._bg)
        self._build_ui()

    def _build_ui(self):
        theme = theme_manager.themes[theme_manager.current_theme]
        bg, fg = self._bg, self._fg

        # Contenedor sin expand para no dejar espacio sobrante debajo
        outer = tk.Frame(self, bg=bg)
        outer.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        # Título
        title = tk.Label(
            outer,
            text="Building Manager Pro",
            font=("Segoe UI", 20, "bold"),
            bg=bg,
            fg=fg,
        )
        title.pack(pady=(0, Spacing.XS))

        subtitle = tk.Label(
            outer,
            text="Inicie sesión para continuar",
            font=("Segoe UI", 10),
            bg=bg,
            fg=theme.get("text_secondary", "#6b7280"),
        )
        subtitle.pack(pady=(0, Spacing.MD))

        # Formulario
        form = tk.Frame(outer, bg=bg)
        form.pack(fill="x", pady=(0, Spacing.SM))

        users = [u for u in user_service.get_all_users() if u.get("is_active")]
        display_options = [f"{u.get('full_name', u.get('username', ''))} ({u.get('username', '')})" for u in users]
        usernames = [u.get("username", "") for u in users]

        tk.Label(form, text="Usuario:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_user = tk.StringVar(value=display_options[0] if display_options else "")
        self._combo = ttk.Combobox(
            form,
            textvariable=self._var_user,
            values=display_options,
            state="readonly",
            font=("Segoe UI", 9),
            width=34,
        )
        self._combo.pack(fill="x", pady=(0, Spacing.SM))
        if display_options:
            self._combo.current(0)

        tk.Label(form, text="Contraseña:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_pass = tk.StringVar()
        self._pass_entry = tk.Entry(
            form,
            textvariable=self._var_pass,
            show="•",
            font=("Segoe UI", 9),
            width=36,
        )
        self._pass_entry.pack(fill="x", pady=(0, Spacing.SM))
        self._pass_entry.bind("<Return>", lambda e: self._do_login())

        self._usernames = usernames
        self._display_options = display_options

        # Botones más arriba, centrados y con hover
        btn_frame = tk.Frame(outer, bg=bg)
        btn_frame.pack(pady=(Spacing.SM, Spacing.XS), anchor="center")

        btn_primary_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_primary_hover = theme.get("btn_primary_hover", "#1d4ed8")
        btn_tertiary = theme.get("bg_tertiary", "#e5e7eb")
        btn_tertiary_hover = "#d1d5db"

        entrar_btn = tk.Button(
            btn_frame,
            text="Entrar",
            font=("Segoe UI", 10),
            bg=btn_primary_bg,
            fg="white",
            activebackground=btn_primary_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=btn_primary_bg,
            highlightcolor=btn_primary_bg,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._do_login,
        )
        entrar_btn.pack(side="left", padx=(0, Spacing.SM))
        entrar_btn.bind("<Enter>", lambda e: entrar_btn.configure(bg=btn_primary_hover))
        entrar_btn.bind("<Leave>", lambda e: entrar_btn.configure(bg=btn_primary_bg))

        salir_btn = tk.Button(
            btn_frame,
            text="Salir",
            font=("Segoe UI", 10),
            bg=btn_tertiary,
            fg=fg,
            activebackground=btn_tertiary_hover,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            highlightbackground=btn_tertiary,
            highlightcolor=btn_tertiary,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._quit,
        )
        salir_btn.pack(side="left")
        salir_btn.bind("<Enter>", lambda e: salir_btn.configure(bg=btn_tertiary_hover))
        salir_btn.bind("<Leave>", lambda e: salir_btn.configure(bg=btn_tertiary))

        # Link "¿Olvidaste tu contraseña?"
        forgot_lbl = tk.Label(
            outer,
            text="¿Olvidaste tu contraseña?",
            font=("Segoe UI", 9, "underline"),
            bg=bg,
            fg=theme.get("btn_primary_bg", "#2563eb"),
            cursor="hand2",
        )
        forgot_lbl.pack(pady=(Spacing.XS, 0))
        forgot_lbl.bind("<Button-1>", lambda e: self._start_password_recovery())
        forgot_lbl.bind("<Enter>", lambda e: forgot_lbl.configure(fg="#1d4ed8"))
        forgot_lbl.bind("<Leave>", lambda e: forgot_lbl.configure(fg=theme.get("btn_primary_bg", "#2563eb")))

    def focus_password_entry(self):
        """Pone el foco en el campo contraseña (llamar tras mostrar la ventana, p. ej. desde main)."""
        self._pass_entry.focus_set()

    def _do_login(self):
        idx = self._combo.current()
        if idx < 0 and self._var_user.get() in self._display_options:
            idx = self._display_options.index(self._var_user.get())
        if idx < 0:
            idx = 0
        username = self._usernames[idx] if idx < len(self._usernames) else (self._usernames[0] if self._usernames else "")
        password = self._var_pass.get().strip()
        if not username:
            messagebox.showwarning("Inicio de sesión", "No hay usuarios en el sistema.", parent=self.winfo_toplevel())
            return
        if not password:
            messagebox.showwarning("Inicio de sesión", "Ingrese la contraseña.", parent=self.winfo_toplevel())
            return
        if not user_service.verify_password(username, password):
            messagebox.showerror("Inicio de sesión", "Contraseña incorrecta.", parent=self.winfo_toplevel())
            return
        user = user_service.get_user_by_username(username)
        if user:
            user_safe = {k: v for k, v in user.items() if k != "password_hash"}
            self.on_success(user_safe)

    def _start_password_recovery(self):
        """Paso 1: confirmar usuario y correo enmascarado, luego enviar código."""
        idx = self._combo.current()
        if idx < 0:
            idx = 0
        username = self._usernames[idx] if idx < len(self._usernames) else ""
        if not username:
            messagebox.showwarning("Recuperar contraseña", "Selecciona un usuario primero.", parent=self.winfo_toplevel())
            return

        # Obtener datos del usuario (con password_hash para acceder al email)
        user_raw = None
        for u in user_service.users:
            if u.get("username") == username:
                user_raw = u
                break

        email = user_raw.get("email", "").strip() if user_raw else ""
        if not email:
            messagebox.showwarning(
                "Recuperar contraseña",
                "Este usuario no tiene un correo registrado.\nContacta al administrador.",
                parent=self.winfo_toplevel(),
            )
            return

        # Enmascarar correo: w***@gmail.com
        parts = email.split("@")
        masked = parts[0][0] + "***@" + parts[1] if len(parts) == 2 and parts[0] else email

        full_name = user_raw.get("full_name", username) if user_raw else username

        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Recuperar contraseña")
        win.resizable(False, False)
        win.grab_set()
        bg = self._bg
        fg = self._fg
        win.configure(bg=bg)

        tk.Label(win, text="Recuperar contraseña", font=("Segoe UI", 13, "bold"), bg=bg, fg=fg).pack(pady=(18, 4), padx=24)
        tk.Label(
            win,
            text=f"Se enviará un código de verificación a:\n{masked}",
            font=("Segoe UI", 10),
            bg=bg,
            fg=fg,
            justify="center",
        ).pack(pady=(0, 14), padx=24)

        btn_frame = tk.Frame(win, bg=bg)
        btn_frame.pack(pady=(0, 18), padx=24)

        theme = theme_manager.themes[theme_manager.current_theme]
        btn_primary_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_primary_hover = theme.get("btn_primary_hover", "#1d4ed8")
        btn_tertiary = theme.get("bg_tertiary", "#e5e7eb")

        def _send():
            win.destroy()
            self._send_code_and_show_dialog(username, email, full_name)

        send_btn = tk.Button(
            btn_frame, text="Enviar código", font=("Segoe UI", 10),
            bg=btn_primary_bg, fg="white", relief="flat", bd=0,
            padx=16, pady=7, cursor="hand2", command=_send,
        )
        send_btn.pack(side="left", padx=(0, 8))
        send_btn.bind("<Enter>", lambda e: send_btn.configure(bg=btn_primary_hover))
        send_btn.bind("<Leave>", lambda e: send_btn.configure(bg=btn_primary_bg))

        cancel_btn = tk.Button(
            btn_frame, text="Cancelar", font=("Segoe UI", 10),
            bg=btn_tertiary, fg=fg, relief="flat", bd=0,
            padx=16, pady=7, cursor="hand2", command=win.destroy,
        )
        cancel_btn.pack(side="left")

        # Centrar ventana
        win.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - win.winfo_width()) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{x}+{y}")

    def _send_code_and_show_dialog(self, username: str, email: str, full_name: str):
        """Genera y envía el código, luego abre el diálogo de verificación."""
        code = user_service.generate_reset_code(username)
        if not code:
            messagebox.showerror("Error", "No se pudo generar el código.", parent=self.winfo_toplevel())
            return

        if not email_service.is_configured():
            messagebox.showwarning(
                "Email no configurado",
                "El servicio de email no está configurado.\nContacta al administrador.",
                parent=self.winfo_toplevel(),
            )
            return

        success, msg = email_service.send_reset_code_email(email, full_name, code)
        if not success:
            logger.warning("Error al enviar código de recuperación: %s", msg)
            messagebox.showerror("Error al enviar", f"No se pudo enviar el correo:\n{msg}", parent=self.winfo_toplevel())
            return

        self._show_code_verification_dialog(username)

    def _show_code_verification_dialog(self, username: str):
        """Paso 2: el usuario ingresa el código y la nueva contraseña."""
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Verificar código")
        win.resizable(False, False)
        win.grab_set()
        bg = self._bg
        fg = self._fg
        win.configure(bg=bg)
        theme = theme_manager.themes[theme_manager.current_theme]
        btn_primary_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_primary_hover = theme.get("btn_primary_hover", "#1d4ed8")
        btn_tertiary = theme.get("bg_tertiary", "#e5e7eb")

        tk.Label(win, text="Ingresa el código recibido", font=("Segoe UI", 13, "bold"), bg=bg, fg=fg).pack(pady=(18, 4), padx=28)
        tk.Label(
            win,
            text="Revisa tu correo. El código expira en 15 minutos.",
            font=("Segoe UI", 9),
            bg=bg,
            fg=theme.get("text_secondary", "#6b7280"),
        ).pack(pady=(0, 12), padx=28)

        form = tk.Frame(win, bg=bg)
        form.pack(fill="x", padx=28, pady=(0, 8))

        tk.Label(form, text="Código:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        var_code = tk.StringVar()
        code_entry = tk.Entry(form, textvariable=var_code, font=("Segoe UI", 14, "bold"), width=12, justify="center")
        code_entry.pack(anchor="w", pady=(0, 10))
        code_entry.focus_set()

        tk.Label(form, text="Nueva contraseña:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        var_pass = tk.StringVar()
        pass_entry = tk.Entry(form, textvariable=var_pass, show="•", font=("Segoe UI", 10), width=28)
        pass_entry.pack(anchor="w", pady=(0, 4))

        tk.Label(form, text="Confirmar contraseña:", font=("Segoe UI", 9), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        var_pass2 = tk.StringVar()
        pass2_entry = tk.Entry(form, textvariable=var_pass2, show="•", font=("Segoe UI", 10), width=28)
        pass2_entry.pack(anchor="w", pady=(0, 4))

        error_lbl = tk.Label(form, text="", font=("Segoe UI", 9), bg=bg, fg="#ef4444")
        error_lbl.pack(anchor="w")

        def _confirm():
            code = var_code.get().strip()
            new_pass = var_pass.get()
            new_pass2 = var_pass2.get()
            if not code:
                error_lbl.configure(text="Ingresa el código.")
                return
            if not new_pass:
                error_lbl.configure(text="Ingresa la nueva contraseña.")
                return
            if new_pass != new_pass2:
                error_lbl.configure(text="Las contraseñas no coinciden.")
                return
            if len(new_pass) < 4:
                error_lbl.configure(text="La contraseña debe tener al menos 4 caracteres.")
                return
            if not user_service.reset_password_with_code(username, code, new_pass):
                error_lbl.configure(text="Código incorrecto o expirado.")
                return
            win.destroy()
            messagebox.showinfo(
                "Contraseña actualizada",
                "Tu contraseña fue actualizada correctamente.\nYa puedes iniciar sesión.",
                parent=self.winfo_toplevel(),
            )

        pass2_entry.bind("<Return>", lambda e: _confirm())

        btn_frame = tk.Frame(win, bg=bg)
        btn_frame.pack(pady=(4, 18), padx=28)

        confirm_btn = tk.Button(
            btn_frame, text="Confirmar", font=("Segoe UI", 10),
            bg=btn_primary_bg, fg="white", relief="flat", bd=0,
            padx=16, pady=7, cursor="hand2", command=_confirm,
        )
        confirm_btn.pack(side="left", padx=(0, 8))
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.configure(bg=btn_primary_hover))
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.configure(bg=btn_primary_bg))

        cancel_btn = tk.Button(
            btn_frame, text="Cancelar", font=("Segoe UI", 10),
            bg=btn_tertiary, fg=fg, relief="flat", bd=0,
            padx=16, pady=7, cursor="hand2", command=win.destroy,
        )
        cancel_btn.pack(side="left")

        # Centrar ventana
        win.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - win.winfo_width()) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{x}+{y}")

    def _quit(self):
        self.winfo_toplevel().quit()
