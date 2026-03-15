#!/usr/bin/env python3
"""
Building Manager Pro - Punto de entrada principal
"""

import tkinter as tk

# Importar paths_config primero para asegurar que esté disponible
import manager.app.paths_config
from manager.app.paths_config import ensure_dirs, get_splash_path
from manager.app.logger import logger
from manager.app.services.user_service import user_service
from manager.app.ui.components.theme_manager import theme_manager
from manager.app.ui.views.main_window import MainWindow
from manager.app.ui.views.login_view import LoginView
from manager.app.ui.views.create_admin_view import CreateAdminView


SPLASH_DURATION_MS = 1200  # 1.2 segundos


def _on_gate_success(root: tk.Tk, user):
    """Tras login o creación de admin: reemplaza la pantalla por la ventana principal."""
    for w in root.winfo_children():
        w.destroy()
    MainWindow(root=root, current_user=user)


def _show_login_or_create_admin(root: tk.Tk):
    """Quita el splash y muestra login o pantalla de crear admin, centrada en pantalla."""
    root.withdraw()  # Ocultar ventana hasta tener tamaño y posición finales (evita destello/arrastre)
    root.overrideredirect(False)  # Restaurar barra de título y bordes para el login
    for w in root.winfo_children():
        w.destroy()
    # Ventana más alta para crear admin (más campos); login más compacto
    is_create_admin = len(user_service.users) == 0
    win_w = 480 if is_create_admin else 440
    win_h = 500 if is_create_admin else 280
    root.minsize(400, 400 if is_create_admin else 260)
    root.resizable(True, True)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - win_w) // 2
    y = (sh - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    if is_create_admin:
        gate = CreateAdminView(root, on_success=lambda u: _on_gate_success(root, u))
    else:
        gate = LoginView(root, on_success=lambda u: _on_gate_success(root, u))
    gate.pack(fill="both", expand=True)
    root.update_idletasks()
    root.deiconify()  # Mostrar ventana ya centrada
    # Foco en contraseña tras un breve retraso (Windows asigna foco al toplevel al mostrarse)
    if hasattr(gate, "focus_password_entry"):
        root.after(150, gate.focus_password_entry)


def main():
    """Función principal que inicia la aplicación."""
    try:
        ensure_dirs()
    except Exception as e:
        logger.warning("No se pudieron crear algunos directorios: %s", e)

    root = tk.Tk()
    root.title("Building Manager Pro")

    try:
        from manager.app.services.app_config_service import app_config_service
        saved_theme = app_config_service.get_theme()
        if saved_theme in ("light", "dark"):
            theme_manager.set_theme(saved_theme)
    except Exception:
        pass

    theme = theme_manager.themes[theme_manager.current_theme]
    root.configure(bg=theme.get("bg_primary", "#ffffff"))

    splash_path = get_splash_path()
    if splash_path:
        try:
            # Sin decoraciones (barra de título/bordes) para que la imagen no se corte
            root.overrideredirect(True)
            root._splash_photo = tk.PhotoImage(file=str(splash_path))
            w, h = root._splash_photo.width(), root._splash_photo.height()
            root.geometry(f"{w}x{h}")
            root.resizable(False, False)
            splash_label = tk.Label(root, image=root._splash_photo, bg=root.cget("bg"))
            splash_label.pack(fill="both", expand=True)
            root.update_idletasks()
            # Centrar ventana en pantalla
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            root.geometry(f"{w}x{h}+{x}+{y}")
            root.after(SPLASH_DURATION_MS, lambda: _show_login_or_create_admin(root))
        except Exception as e:
            logger.warning("No se pudo mostrar splash: %s", e)
            _show_login_or_create_admin(root)
    else:
        _show_login_or_create_admin(root)

    root.mainloop()


if __name__ == "__main__":
    main()
