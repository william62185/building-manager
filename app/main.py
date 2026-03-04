#!/usr/bin/env python3
"""
Building Manager Pro - Punto de entrada principal
"""

import tkinter as tk

# Importar paths_config primero para asegurar que esté disponible
import manager.app.paths_config
from manager.app.paths_config import ensure_dirs
from manager.app.services.user_service import user_service
from manager.app.ui.components.theme_manager import theme_manager
from manager.app.ui.views.main_window import MainWindow
from manager.app.ui.views.login_view import LoginView
from manager.app.ui.views.create_admin_view import CreateAdminView


def _on_gate_success(root: tk.Tk, user):
    """Tras login o creación de admin: reemplaza la pantalla por la ventana principal."""
    for w in root.winfo_children():
        w.destroy()
    MainWindow(root=root, current_user=user)


def main():
    """Función principal que inicia la aplicación."""
    try:
        ensure_dirs()
    except Exception as e:
        print(f"Advertencia: No se pudieron crear algunos directorios: {e}")

    root = tk.Tk()
    root.title("Building Manager Pro")
    root.geometry("440x280")
    root.minsize(400, 260)
    root.resizable(True, True)

    try:
        from manager.app.services.app_config_service import app_config_service
        saved_theme = app_config_service.get_theme()
        if saved_theme in ("light", "dark"):
            theme_manager.set_theme(saved_theme)
    except Exception:
        pass

    theme = theme_manager.themes[theme_manager.current_theme]
    root.configure(bg=theme.get("bg_primary", "#ffffff"))

    if len(user_service.users) == 0:
        gate = CreateAdminView(root, on_success=lambda u: _on_gate_success(root, u))
    else:
        gate = LoginView(root, on_success=lambda u: _on_gate_success(root, u))

    gate.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
