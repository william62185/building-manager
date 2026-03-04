"""
Vista para crear el primer usuario administrador.
Se muestra al arrancar la app cuando no hay usuarios (primera instalación).
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Any

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.user_service import user_service


class CreateAdminView(tk.Frame):
    """Pantalla para crear el usuario administrador inicial. Al crear llama on_success(user)."""

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

        # Título y bienvenida
        title = tk.Label(
            self,
            text="Building Manager Pro",
            font=("Segoe UI", 22, "bold"),
            bg=bg,
            fg=fg,
        )
        title.pack(pady=(Spacing.XXL, Spacing.SM))

        welcome = tk.Label(
            self,
            text="Bienvenido. Cree el usuario administrador para comenzar.",
            font=("Segoe UI", 11),
            bg=bg,
            fg=theme.get("text_secondary", "#6b7280"),
        )
        welcome.pack(pady=(0, Spacing.LG))

        # Formulario
        form = tk.Frame(self, bg=bg)
        form.pack(fill="x", padx=Spacing.XXL, pady=Spacing.MD)

        tk.Label(form, text="Nombre completo:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_full_name = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self._var_full_name,
            font=("Segoe UI", 10),
            width=40,
        ).pack(fill="x", pady=(0, Spacing.SM))

        tk.Label(form, text="Usuario (inicio de sesión):", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_username = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self._var_username,
            font=("Segoe UI", 10),
            width=40,
        ).pack(fill="x", pady=(0, Spacing.SM))

        tk.Label(form, text="Contraseña:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_pass = tk.StringVar()
        pass_entry = tk.Entry(
            form,
            textvariable=self._var_pass,
            show="•",
            font=("Segoe UI", 10),
            width=40,
        )
        pass_entry.pack(fill="x", pady=(0, Spacing.SM))

        tk.Label(form, text="Confirmar contraseña:", font=("Segoe UI", 10), bg=bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_confirm = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self._var_confirm,
            show="•",
            font=("Segoe UI", 10),
            width=40,
        ).pack(fill="x", pady=(0, Spacing.LG))

        # Botones
        btn_frame = tk.Frame(self, bg=bg)
        btn_frame.pack(fill="x", padx=Spacing.XXL, pady=Spacing.LG)

        tk.Button(
            btn_frame,
            text="Crear administrador",
            font=("Segoe UI", 10),
            bg=theme.get("btn_primary_bg", "#2563eb"),
            fg="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._do_create,
        ).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(
            btn_frame,
            text="Salir",
            font=("Segoe UI", 10),
            bg=theme.get("bg_tertiary", "#e5e7eb"),
            fg=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._quit,
        ).pack(side="left")

    def _do_create(self):
        full_name = self._var_full_name.get().strip()
        username = self._var_username.get().strip()
        password = self._var_pass.get().strip()
        confirm = self._var_confirm.get().strip()

        if not full_name:
            messagebox.showwarning("Crear administrador", "Ingrese el nombre completo.", parent=self.winfo_toplevel())
            return
        if not username:
            messagebox.showwarning("Crear administrador", "Ingrese el nombre de usuario.", parent=self.winfo_toplevel())
            return
        if not password:
            messagebox.showwarning("Crear administrador", "Ingrese la contraseña.", parent=self.winfo_toplevel())
            return
        if password != confirm:
            messagebox.showwarning("Crear administrador", "Las contraseñas no coinciden.", parent=self.winfo_toplevel())
            return
        if len(password) < 4:
            messagebox.showwarning("Crear administrador", "La contraseña debe tener al menos 4 caracteres.", parent=self.winfo_toplevel())
            return

        try:
            user = user_service.create_user(
                {
                    "username": username,
                    "full_name": full_name,
                    "email": "",
                    "password": password,
                    "role": "admin",
                    "is_active": True,
                },
                created_by="system",
            )
            user_safe = {k: v for k, v in user.items() if k != "password_hash"}
            self.on_success(user_safe)
        except ValueError as e:
            messagebox.showerror("Crear administrador", str(e), parent=self.winfo_toplevel())

    def _quit(self):
        self.winfo_toplevel().quit()
