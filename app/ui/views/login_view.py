"""
Vista de inicio de sesión.
Se muestra al arrancar la app cuando ya existen usuarios.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Callable, Dict, Any

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.user_service import user_service


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
        self._pass_entry.focus_set()
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

    def _quit(self):
        self.winfo_toplevel().quit()
