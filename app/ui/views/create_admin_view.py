"""
Vista para crear el primer usuario administrador.
Se muestra al arrancar la app cuando no hay usuarios (primera instalación).
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Any

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.user_service import user_service


def _styled_entry(parent, textvariable, show=None, width=36, **kwargs):
    """Crea un Entry con borde visible y estilo consistente."""
    theme = theme_manager.themes[theme_manager.current_theme]
    f = tk.Frame(parent, bg=theme.get("bg_primary", "#ffffff"))
    entry = tk.Entry(
        f,
        textvariable=textvariable,
        font=("Segoe UI", 10),
        width=width,
        relief="solid",
        bd=1,
        bg=theme.get("bg_primary", "#ffffff"),
        fg=theme.get("text_primary", "#1e293b"),
        highlightthickness=0,
        **(dict(show=show) if show else {}),
        **kwargs,
    )
    entry.pack(fill="x", padx=1, pady=1, ipady=4, ipadx=6)
    return f, entry


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
        header_bg = theme.get("header_bg", "#8B4513")
        card_bg = theme.get("bg_tertiary", "#f1f5f9")
        secondary = theme.get("text_secondary", "#6b7280")

        # Barra superior compacta (regla de compactación)
        header = tk.Frame(self, bg=header_bg)
        header.pack(fill="x", pady=(0, Spacing.MD))
        tk.Label(
            header,
            text="Building Manager Pro",
            font=("Segoe UI", 16, "bold"),
            bg=header_bg,
            fg="white",
        ).pack(pady=Spacing.SM, padx=Spacing.LG)
        tk.Label(
            header,
            text="Crear usuario administrador",
            font=("Segoe UI", 10),
            bg=header_bg,
            fg="#ffffff",
        ).pack(pady=(0, Spacing.SM), padx=Spacing.LG)

        # Contenedor del formulario (compactación: sin scroll)
        outer = tk.Frame(self, bg=bg, padx=Spacing.LG, pady=Spacing.SM)
        outer.pack(fill="both", expand=True)

        # Texto de bienvenida: wraplength para que no se recorte al inicio/final
        welcome = tk.Label(
            outer,
            text="Bienvenido. Complete los datos para crear el primer administrador.",
            font=("Segoe UI", 10),
            bg=bg,
            fg=secondary,
            wraplength=400,
            justify="left",
        )
        welcome.pack(anchor="w", pady=(0, Spacing.SM))

        # Card del formulario (compactación)
        card = tk.Frame(outer, bg=card_bg, relief="solid", bd=1)
        card.pack(fill="x", pady=(0, Spacing.MD))
        form = tk.Frame(card, bg=card_bg, padx=Spacing.MD, pady=Spacing.MD)
        form.pack(fill="x")

        # Nombre completo
        tk.Label(form, text="Nombre completo:", font=("Segoe UI", 9), bg=card_bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_full_name = tk.StringVar()
        fe1, self._entry_full = _styled_entry(form, self._var_full_name)
        fe1.pack(fill="x", pady=(0, Spacing.SM))

        # Usuario
        tk.Label(form, text="Usuario (inicio de sesión):", font=("Segoe UI", 9), bg=card_bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_username = tk.StringVar()
        fe2, self._entry_user = _styled_entry(form, self._var_username)
        fe2.pack(fill="x", pady=(0, Spacing.SM))

        # Contraseña
        tk.Label(form, text="Contraseña:", font=("Segoe UI", 9), bg=card_bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_pass = tk.StringVar()
        fe3, self._entry_pass = _styled_entry(form, self._var_pass, show="•")
        fe3.pack(fill="x", pady=(0, Spacing.SM))

        # Confirmar contraseña
        tk.Label(form, text="Confirmar contraseña:", font=("Segoe UI", 9), bg=card_bg, fg=fg).pack(anchor="w", pady=(0, 2))
        self._var_confirm = tk.StringVar()
        fe4, self._entry_confirm = _styled_entry(form, self._var_confirm, show="•")
        fe4.pack(fill="x", pady=(0, Spacing.SM))
        self._entry_confirm.bind("<Return>", lambda e: self._do_create())

        # Botones
        btn_frame = tk.Frame(outer, bg=bg)
        btn_frame.pack(fill="x", pady=(Spacing.SM, 0))

        btn_primary_bg = theme.get("btn_primary_bg", "#2563eb")
        btn_primary_hover = theme.get("btn_primary_hover", "#1d4ed8")
        btn_tertiary = theme.get("bg_tertiary", "#e5e7eb")
        btn_tertiary_hover = "#d1d5db"

        crear_btn = tk.Button(
            btn_frame,
            text="  Crear administrador  ",
            font=("Segoe UI", 10),
            bg=btn_primary_bg,
            fg="white",
            activebackground=btn_primary_hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._do_create,
        )
        crear_btn.pack(side="left", padx=(0, Spacing.SM))
        crear_btn.bind("<Enter>", lambda e: crear_btn.configure(bg=btn_primary_hover))
        crear_btn.bind("<Leave>", lambda e: crear_btn.configure(bg=btn_primary_bg))

        salir_btn = tk.Button(
            btn_frame,
            text="  Salir  ",
            font=("Segoe UI", 10),
            bg=btn_tertiary,
            fg=fg,
            activebackground=btn_tertiary_hover,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._quit,
        )
        salir_btn.pack(side="left")
        salir_btn.bind("<Enter>", lambda e: salir_btn.configure(bg=btn_tertiary_hover))
        salir_btn.bind("<Leave>", lambda e: salir_btn.configure(bg=btn_tertiary))

        self.after(200, self._entry_full.focus_set)

    def focus_password_entry(self):
        """Pone el foco en el campo de contraseña (usado desde main al mostrar la ventana)."""
        self._entry_pass.focus_set()

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
