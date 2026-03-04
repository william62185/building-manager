"""
Vista para gestión de usuarios del sistema
Permite crear, editar, eliminar usuarios y ver historial de actividad
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from datetime import datetime

from manager.app.services.user_service import user_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernCard, create_rounded_button, get_module_colors


class UserManagementView(tk.Frame):
    """Vista para gestión de usuarios del sistema"""

    def __init__(self, parent, on_back: Callable = None, on_navigate: Callable = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate = on_navigate
        self.current_view = "list"
        self.editing_user_id = None
        self._create_layout()
        self._load_users_list()

    def _create_layout(self):
        """Crea el layout principal"""
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        fg = theme.get("text_primary", "#1f2937")
        header = tk.Frame(self, bg=cb)
        header.pack(fill="x", pady=(0, 0), padx=Spacing.MD)
        title = tk.Label(header, text="Gestión de Usuarios", font=("Segoe UI", 16, "bold"), bg=cb, fg=fg)
        title.pack(side="left")
        buttons_frame = tk.Frame(header, bg=cb)
        buttons_frame.pack(side="right")
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        btn_bg = theme.get("btn_secondary_bg", "#e5e7eb")

        def go_to_dashboard():
            if self.on_navigate:
                self.on_navigate("dashboard")
            elif self.on_back:
                self.on_back()

        def go_back():
            if self.current_view != "list":
                self._show_users_list()
            elif self.on_back:
                self.on_back()

        btn_volver = create_rounded_button(
            buttons_frame,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=btn_bg,
            fg_color=purple_primary,
            hover_bg=purple_light,
            hover_fg=purple_text,
            command=go_back,
            padx=16,
            pady=8,
            radius=4,
            border_color=purple_light
        )
        btn_volver.pack(side="right", padx=(Spacing.MD, 0))
        btn_dashboard = create_rounded_button(
            buttons_frame,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color=purple_hover
        )
        btn_dashboard.pack(side="right")
        self.main_container = tk.Frame(self, bg=cb)
        self.main_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))
    
    def _show_users_list(self):
        """Muestra la lista de usuarios"""
        self.current_view = "list"
        self.editing_user_id = None
        
        # Limpiar contenedor
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        self._load_users_list()
    
    def _load_users_list(self):
        """Carga y muestra la lista de usuarios. Limpia el contenedor antes para evitar duplicados al refrescar."""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        cb = self._content_bg
        fg_sec = "#374151"
        container = tk.Frame(self.main_container, bg=cb)
        container.pack(fill="both", expand=True)
        list_header = tk.Frame(container, bg=cb)
        list_header.pack(fill="x", pady=(Spacing.MD, Spacing.MD))
        stats = user_service.get_user_count()
        stats_label = tk.Label(
            list_header,
            text=f"Total: {stats['total']} | Activos: {stats['active']} | Inactivos: {stats['inactive']}",
            font=("Segoe UI", 10),
            fg=fg_sec,
            bg=cb
        )
        stats_label.pack(side="left")
        
        btn_create = tk.Button(
            list_header,
            text=f"{Icons.ADD} Crear Usuario",
            font=("Segoe UI", 10, "bold"),
            bg="#8b5cf6",  # Morado para mantener tonalidad morada del módulo de administración
            fg="white",
            activebackground="#7c3aed",  # Morado oscuro para hover
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=Spacing.MD,
            pady=Spacing.SM,
            cursor="hand2",
            command=self._show_create_user_form
        )
        btn_create.pack(side="right", padx=(Spacing.MD, 0))
        
        canvas = tk.Canvas(container, bg=cb, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=cb)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def update_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", update_canvas_width)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar usuarios
        users = user_service.get_all_users()
        
        if not users:
            no_users_label = tk.Label(
                scrollable_frame,
                text="No hay usuarios registrados",
                font=("Segoe UI", 12),
                fg="#6b7280",
                bg=cb
            )
            no_users_label.pack(pady=Spacing.XL)
        else:
            for user in users:
                self._create_user_card(scrollable_frame, user)
    
    def _create_user_card(self, parent, user: dict):
        """Crea un elemento de lista para mostrar información de un usuario"""
        card_bg = "#f3e8ff"
        list_item = tk.Frame(parent, bg=card_bg, relief="flat", bd=0)
        list_item.pack(fill="x", pady=(0, 2))
        content = tk.Frame(list_item, bg=card_bg)
        content.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        main_row = tk.Frame(content, bg=card_bg)
        main_row.pack(fill="x", pady=(0, 0))
        info_frame = tk.Frame(main_row, bg=card_bg)
        info_frame.pack(side="left", fill="x", expand=True)
        name_label = tk.Label(
            info_frame,
            text=f"👤 {user.get('full_name', 'N/A')} (@{user.get('username', 'N/A')})",
            font=("Segoe UI", 10, "bold"),
            fg="#1f2937",
            bg=card_bg,
            anchor="w"
        )
        name_label.pack(anchor="w")
        email = user.get('email', 'N/A')
        role = user_service.ROLES.get(user.get('role', ''), user.get('role', 'N/A'))
        status = "✅ Activo" if user.get('is_active') else "❌ Inactivo"
        details_label = tk.Label(
            info_frame,
            text=f"📧 {email} | 🎭 {role} | {status}",
            font=("Segoe UI", 9),
            fg="#374151",
            bg=card_bg,
            anchor="w"
        )
        details_label.pack(anchor="w", pady=(1, 0))
        buttons_frame = tk.Frame(main_row, bg=card_bg)
        buttons_frame.pack(side="right", padx=(Spacing.SM, 0))
        
        btn_edit = tk.Button(
            buttons_frame,
            text=f"{Icons.EDIT} Editar",
            font=("Segoe UI", 8),
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda uid=user.get('id'): self._show_edit_user_form(uid)
        )
        btn_edit.pack(side="left", padx=(0, 3))
        
        btn_password = tk.Button(
            buttons_frame,
            text=f"🔑 Contraseña",
            font=("Segoe UI", 8),
            bg="#f59e0b",
            fg="white",
            activebackground="#d97706",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda uid=user.get('id'): self._show_change_password_dialog(uid)
        )
        btn_password.pack(side="left", padx=(0, 3))
        
        btn_activity = tk.Button(
            buttons_frame,
            text=f"📋 Actividad",
            font=("Segoe UI", 8),
            bg="#8b5cf6",
            fg="white",
            activebackground="#7c3aed",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda uid=user.get('id'), uname=user.get('username'): self._show_activity_log(uid, uname)
        )
        btn_activity.pack(side="left", padx=(0, 3))
        
        btn_delete = tk.Button(
            buttons_frame,
            text=f"{Icons.DELETE} Eliminar",
            font=("Segoe UI", 8),
            bg="#ef4444",
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda uid=user.get('id'), uname=user.get('username'): self._delete_user(uid, uname)
        )
        btn_delete.pack(side="left")
        
        # Separador sutil entre elementos (excepto el último)
        separator = tk.Frame(
            list_item,
            height=1,
            bg="#e0e0e0"
        )
        separator.pack(fill="x", padx=Spacing.SM)
    
    def _show_create_user_form(self):
        """Muestra el formulario para crear un nuevo usuario"""
        self.current_view = "form"
        self.editing_user_id = None
        self._show_user_form()
    
    def _show_edit_user_form(self, user_id: int):
        """Muestra el formulario para editar un usuario"""
        self.current_view = "form"
        self.editing_user_id = user_id
        self._show_user_form()
    
    def _show_user_form(self):
        """Muestra el formulario de usuario (crear o editar)"""
        # Limpiar contenedor
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        card = ModernCard(self.main_container, bg=self._content_bg)
        card.pack(fill="x", anchor="n", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        content = tk.Frame(card, bg=cb)
        content.pack(fill="x", padx=Spacing.MD, pady=Spacing.XS)
        title_text = "Editar Usuario" if self.editing_user_id else "Crear Nuevo Usuario"
        title = tk.Label(content, text=title_text, font=("Segoe UI", 14, "bold"), fg=fg, bg=cb)
        title.pack(anchor="w", pady=(0, 2))
        user_data = None
        if self.editing_user_id:
            user_data = user_service.get_user_by_id(self.editing_user_id)
        form_frame = tk.Frame(content, bg=cb)
        form_frame.pack(fill="x", pady=(0, 2))
        tk.Label(form_frame, text="Nombre de Usuario *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        username_var = tk.StringVar(value=user_data.get('username', '') if user_data else '')
        username_entry = tk.Entry(form_frame, textvariable=username_var, font=("Segoe UI", 9), width=50)
        username_entry.pack(anchor="w", pady=(0, 1))
        
        tk.Label(form_frame, text="Email *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        email_var = tk.StringVar(value=user_data.get('email', '') if user_data else '')
        email_entry = tk.Entry(form_frame, textvariable=email_var, font=("Segoe UI", 9), width=50)
        email_entry.pack(anchor="w", pady=(0, 1))
        tk.Label(form_frame, text="Nombre Completo *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        full_name_var = tk.StringVar(value=user_data.get('full_name', '') if user_data else '')
        full_name_entry = tk.Entry(form_frame, textvariable=full_name_var, font=("Segoe UI", 9), width=50)
        full_name_entry.pack(anchor="w", pady=(0, 1))
        password_var = tk.StringVar()
        if not self.editing_user_id:
            tk.Label(form_frame, text="Contraseña *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
            password_entry = tk.Entry(form_frame, textvariable=password_var, font=("Segoe UI", 9), width=50, show="*")
            password_entry.pack(anchor="w", pady=(0, 1))
        tk.Label(form_frame, text="Rol *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        role_var = tk.StringVar(value=user_data.get('role', 'viewer') if user_data else 'viewer')
        role_combo = ttk.Combobox(
            form_frame,
            textvariable=role_var,
            values=list(user_service.ROLES.keys()),
            state="readonly",
            font=("Segoe UI", 9),
            width=47
        )
        role_combo.pack(anchor="w", pady=(0, 1))
        
        is_active_var = tk.BooleanVar(value=user_data.get('is_active', True) if user_data else True)
        active_check = tk.Checkbutton(form_frame, text="Usuario Activo", variable=is_active_var, font=("Segoe UI", 9), fg=fg, bg=cb, activebackground=cb, activeforeground=fg, selectcolor=cb)
        active_check.pack(anchor="w", pady=(0, 1))
        tk.Label(form_frame, text="Notas", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        notes_text = tk.Text(form_frame, font=("Segoe UI", 9), width=50, height=1)
        notes_text.pack(anchor="w", pady=(0, 2))
        if user_data and user_data.get('notes'):
            notes_text.insert("1.0", user_data.get('notes'))
        buttons_frame = tk.Frame(content, bg=cb)
        buttons_frame.pack(fill="x", pady=(2, 0))
        
        def save_user():
            try:
                user_data = {
                    "username": username_var.get().strip(),
                    "email": email_var.get().strip(),
                    "full_name": full_name_var.get().strip(),
                    "role": role_var.get(),
                    "is_active": is_active_var.get(),
                    "notes": notes_text.get("1.0", tk.END).strip()
                }
                
                if not user_data["username"]:
                    messagebox.showerror("Error", "El nombre de usuario es requerido")
                    return
                
                if not user_data["email"]:
                    messagebox.showerror("Error", "El email es requerido")
                    return
                
                if not user_data["full_name"]:
                    messagebox.showerror("Error", "El nombre completo es requerido")
                    return
                
                if self.editing_user_id:
                    # Actualizar usuario
                    user_service.update_user(self.editing_user_id, user_data, updated_by="admin")
                    messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                else:
                    # Crear usuario
                    password = password_var.get()
                    if not password:
                        messagebox.showerror("Error", "La contraseña es requerida")
                        return
                    
                    user_data["password"] = password
                    user_service.create_user(user_data, created_by="admin")
                    messagebox.showinfo("Éxito", "Usuario creado correctamente")
                
                self._show_users_list()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar usuario: {str(e)}")
        
        btn_save = tk.Button(
            buttons_frame,
            text=f"{Icons.SAVE} Guardar",
            font=("Segoe UI", 9, "bold"),
            bg="#8b5cf6",  # Morado para mantener tonalidad morada del módulo de administración
            fg="white",
            activebackground="#7c3aed",  # Morado oscuro para hover
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=Spacing.SM,
            pady=4,
            cursor="hand2",
            command=save_user
        )
        btn_save.pack(side="left", padx=(0, Spacing.XS))
        
        btn_cancel = tk.Button(
            buttons_frame,
            text=f"{Icons.CANCEL} Cancelar",
            font=("Segoe UI", 9, "bold"),
            bg="#6b7280",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=Spacing.SM,
            pady=4,
            cursor="hand2",
            command=self._show_users_list
        )
        btn_cancel.pack(side="left")
    
    def _show_change_password_dialog(self, user_id: int):
        """Diálogo compacto para cambiar contraseña; sin espacio sobrante para que no se vea contenido de fondo."""
        user = user_service.get_user_by_id(user_id)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        colors = get_module_colors("administración")
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = theme.get("bg_secondary", self._content_bg)
        fg = theme.get("text_primary", "#1f2937")

        dialog = tk.Toplevel(self)
        dialog.title("Cambiar Contraseña")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=cb)

        # Cabecera compacta
        header_bg = colors.get("primary", "#8b5cf6")
        header = tk.Frame(dialog, bg=header_bg, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="  Cambiar Contraseña", font=("Segoe UI", 11, "bold"), bg=header_bg, fg="white").pack(side="left", pady=8)

        # Formulario compacto (sin expand para no dejar hueco abajo)
        form_frame = tk.Frame(dialog, bg=cb)
        form_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        username_display = user.get("full_name", user.get("username", ""))
        tk.Label(form_frame, text=f"Usuario: {username_display}", font=("Segoe UI", 9), fg=fg, bg=cb).pack(anchor="w", pady=(0, Spacing.SM))
        tk.Label(form_frame, text="Nueva contraseña *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        password_var = tk.StringVar()
        password_entry = tk.Entry(form_frame, textvariable=password_var, font=("Segoe UI", 10), width=38, show="•")
        password_entry.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(form_frame, text="Confirmar contraseña *", font=("Segoe UI", 9, "bold"), fg=fg, bg=cb).pack(anchor="w", pady=(0, 1))
        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(form_frame, textvariable=confirm_var, font=("Segoe UI", 10), width=38, show="•")
        confirm_entry.pack(fill="x", pady=(0, 0))
        password_entry.focus_set()

        def change_password():
            password = password_var.get().strip()
            confirm = confirm_var.get().strip()
            if not password:
                messagebox.showerror("Error", "La contraseña es requerida.", parent=dialog)
                return
            if password != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=dialog)
                return
            if len(password) < 6:
                messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.", parent=dialog)
                return
            try:
                user_service.change_password(user_id, password, changed_by="admin")
                messagebox.showinfo("Éxito", "Contraseña cambiada correctamente.", parent=dialog)
                dialog.destroy()
                self._load_users_list()
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=dialog)

        def on_cancel():
            dialog.destroy()

        # Botones pegados al formulario, sin espacio extra
        btn_opts = dict(font=("Segoe UI", 10), relief="flat", bd=0, highlightthickness=0, padx=16, pady=6, cursor="hand2")
        btn_frame = tk.Frame(dialog, bg=cb)
        btn_frame.pack(fill="x", padx=Spacing.LG, pady=(Spacing.SM, Spacing.MD))
        tk.Button(btn_frame, text="Aceptar", bg=colors.get("primary", "#8b5cf6"), fg="white", **btn_opts, command=change_password).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btn_frame, text="Cancelar", bg=theme.get("bg_tertiary", "#6b7280"), fg="white", **btn_opts, command=on_cancel).pack(side="left")

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        # Tamaño justo al contenido para ventana compacta y sin hueco que muestre lo de atrás
        dialog.update_idletasks()
        w, h = 400, 268
        x = (dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    def _show_activity_log(self, user_id: int, username: str):
        """Muestra el historial de actividad de un usuario"""
        self.current_view = "activity"
        
        # Limpiar contenedor
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        card = ModernCard(self.main_container, bg=self._content_bg)
        card.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        content = tk.Frame(card, bg=cb)
        content.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        title = tk.Label(content, text=f"Historial de Actividad: {username}", font=("Segoe UI", 16, "bold"), fg=fg, bg=cb)
        title.pack(anchor="w", pady=(0, Spacing.MD))
        canvas = tk.Canvas(content, bg=cb, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=cb)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def update_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", update_canvas_width)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar actividad
        activities = user_service.get_activity_log(username=username, limit=100)
        
        if not activities:
            tk.Label(scrollable_frame, text="No hay actividad registrada", font=("Segoe UI", 11), fg="#6b7280", bg=cb).pack(pady=Spacing.XL)
        else:
            for activity in activities:
                self._create_activity_item(scrollable_frame, activity)
    
    def _create_activity_item(self, parent, activity: dict):
        """Crea un elemento de actividad"""
        cb = self._content_bg
        item_frame = tk.Frame(parent, bg=cb)
        item_frame.pack(fill="x", pady=(0, Spacing.SM))
        timestamp = activity.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp)
            timestamp_str = dt.strftime("%d/%m/%Y %H:%M:%S")
        except:
            timestamp_str = timestamp
        action = activity.get('action', '')
        action_labels = {
            'user_created': '👤 Usuario creado',
            'user_updated': '✏️ Usuario actualizado',
            'user_deleted': '🗑️ Usuario eliminado',
            'password_changed': '🔑 Contraseña cambiada'
        }
        action_label = action_labels.get(action, f"📋 {action}")
        details = activity.get('details', '')
        username = activity.get('username', 'N/A')
        info_text = f"{timestamp_str} | {action_label} | {details}"
        if activity.get('target_user') and activity.get('target_user') != username:
            info_text += f" | Usuario objetivo: {activity.get('target_user')}"
        tk.Label(item_frame, text=info_text, font=("Segoe UI", 9), fg="#374151", bg=cb, anchor="w", wraplength=800).pack(anchor="w")
        separator = tk.Frame(item_frame, height=1, bg="#e5e7eb")
        separator.pack(fill="x", pady=(Spacing.SM, 0))
    
    def _delete_user(self, user_id: int, username: str):
        """Elimina (desactiva) un usuario"""
        user = user_service.get_user_by_id(user_id)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado")
            return
        
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar (desactivar) al usuario '{username}'?\n\n"
            f"Esta acción marcará al usuario como inactivo.",
            icon="warning"
        )
        
        if not confirm:
            return
        
        try:
            user_service.delete_user(user_id, deleted_by="admin")
            messagebox.showinfo("Éxito", f"Usuario '{username}' eliminado (desactivado) correctamente")
            self._load_users_list()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")
